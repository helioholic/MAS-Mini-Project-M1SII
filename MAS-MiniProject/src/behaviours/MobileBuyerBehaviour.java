package behaviours;

import jade.core.AID;
import jade.core.ContainerID;
import jade.core.behaviours.Behaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;
import models.Offer;
import utils.Constants;

import java.util.ArrayList;
import java.util.List;
import java.io.Serializable;

public class MobileBuyerBehaviour extends Behaviour implements Serializable {

    private jade.core.Agent buyer;
    private List<String> sellerNames;     // names of sellers to visit
    private List<String> containerNames;  // container of each seller
    private List<Offer> collectedOffers;  // offers collected so far

    private int currentIndex = 0;         // which seller we're visiting now
    private int phase = 0;                // 0=travel, 1=request, 2=wait reply, 3=done
    private boolean done = false;

    public MobileBuyerBehaviour(jade.core.Agent buyer,
            List<String> sellerNames,
            List<String> containerNames) {
        super(buyer);
        this.buyer = buyer;
        this.sellerNames = sellerNames;
        this.containerNames = containerNames;
        this.collectedOffers = new ArrayList<>();
    }

    @Override
    public void action() {

        // ── PHASE 0: Travel to next seller's container ───────────────
        if (phase == 0) {
            if (currentIndex < sellerNames.size()) {
                String targetContainer = containerNames.get(currentIndex);
                System.out.println("\n[MobileBuyer] Travelling to container: "
                        + targetContainer);

                // doMove() is the key JADE method for agent migration!
                buyer.doMove(new ContainerID(targetContainer, null));
                phase = 1; // after move, go to request phase
            } else {
                // visited all sellers → go back home
                System.out.println("\n[MobileBuyer] All sellers visited. Returning home...");
                buyer.doMove(new ContainerID("Main-Container", null));
                phase = 3; // final phase: compute results
            }
        } // ── PHASE 1: Send REQUEST to seller in this container ────────
        else if (phase == 1) {
            String sellerName = sellerNames.get(currentIndex);
            System.out.println("[MobileBuyer] Arrived at container: "
                    + buyer.here().getName());
            System.out.println("[MobileBuyer] Requesting offer from: " + sellerName);

            ACLMessage request = new ACLMessage(ACLMessage.REQUEST);
            request.addReceiver(new AID(sellerName, AID.ISLOCALNAME));
            request.setContent(Constants.REQUEST_OFFER);
            request.setConversationId("part2-" + sellerName);
            buyer.send(request);

            phase = 2; // now wait for reply
        } // ── PHASE 2: Wait for INFORM reply ───────────────────────────
        else if (phase == 2) {
            String sellerName = sellerNames.get(currentIndex);
            MessageTemplate mt = MessageTemplate.and(
                    MessageTemplate.MatchPerformative(ACLMessage.INFORM),
                    MessageTemplate.MatchConversationId("part2-" + sellerName)
            );

            ACLMessage reply = buyer.receive(mt);

            if (reply != null) {
                // Parse "price:quality:deliveryCost"
                String[] parts = reply.getContent().split(":");
                double price = Double.parseDouble(parts[0]);
                double quality = Double.parseDouble(parts[1]);
                double deliveryCost = Double.parseDouble(parts[2]);

                Offer offer = new Offer(sellerName, price, quality, deliveryCost);
                collectedOffers.add(offer);

                System.out.println("[MobileBuyer] Received offer: " + offer);

                currentIndex++; // next seller
                phase = 0;      // travel to next
            } else {
                block(2000); // wait for reply
            }
        } // ── PHASE 3: Back home — compute scores ──────────────────────
        else if (phase == 3) {
            System.out.println("\n[MobileBuyer] Back in: " + buyer.here().getName());
            System.out.println("[MobileBuyer] Computing scores for "
                    + collectedOffers.size() + " offers...\n");

            computeAndAnnounce();
            done = true;
            buyer.doDelete();
        }
    }

    // ── Score computation ─────────────────────────────────────────────
    private void computeAndAnnounce() {
        // Step 1: find min/max values across all offers for normalization
        double minPrice = Double.MAX_VALUE, maxPrice = Double.MIN_VALUE;
        double minQuality = Double.MAX_VALUE, maxQuality = Double.MIN_VALUE;
        double minDelivery = Double.MAX_VALUE, maxDelivery = Double.MIN_VALUE;

        for (Offer o : collectedOffers) {
            minPrice = Math.min(minPrice, o.getPrice());
            maxPrice = Math.max(maxPrice, o.getPrice());
            minQuality = Math.min(minQuality, o.getQuality());
            maxQuality = Math.max(maxQuality, o.getQuality());
            minDelivery = Math.min(minDelivery, o.getDeliveryCost());
            maxDelivery = Math.max(maxDelivery, o.getDeliveryCost());
        }

        // Step 2: compute f(x) for each offer
        Offer bestOffer = null;
        double bestScore = -1;

        System.out.println("[MobileBuyer] ╔══════════════════════════════════════════╗");
        System.out.println("[MobileBuyer] ║           OFFER EVALUATION               ║");
        System.out.println("[MobileBuyer] ╠══════════════════════════════════════════╣");

        for (Offer o : collectedOffers) {
            // Normalize: MINIMIZE → minVal/val, MAXIMIZE → val/maxVal
            double normPrice = minPrice / o.getPrice();       // minimize
            double normQuality = o.getQuality() / maxQuality;   // maximize
            double normDelivery = minDelivery / o.getDeliveryCost();// minimize

            // f(x) = Σ normalized(Ci) × preference(Ci)
            double score = normPrice * Constants.PREF_PRICE
                    + normQuality * Constants.PREF_QUALITY
                    + normDelivery * Constants.PREF_DELIVERY;

            System.out.printf("[MobileBuyer] ║ %-10s → normP=%.3f normQ=%.3f normD=%.3f║%n",
                    o.getSellerName(), normPrice, normQuality, normDelivery);
            System.out.printf("[MobileBuyer] ║             f(x) = %.4f"
                    + "                       ║%n", score);
            System.out.println("[MobileBuyer] ╠══════════════════════════════════════════╣");

            if (score > bestScore) {
                bestScore = score;
                bestOffer = o;
            }
        }

        // Step 3: announce winner
        System.out.println("[MobileBuyer] ║         BEST OFFER                       ║");
        System.out.println("[MobileBuyer] ╠══════════════════════════════════════════╣");
        System.out.printf("[MobileBuyer] ║ Seller  : %-32s║%n", bestOffer.getSellerName());
        System.out.printf("[MobileBuyer] ║ Price   : %-32s║%n", String.format("%.2f", bestOffer.getPrice()));
        System.out.printf("[MobileBuyer] ║ Quality : %-32s║%n", String.format("%.2f", bestOffer.getQuality()));
        System.out.printf("[MobileBuyer] ║ Delivery: %-32s║%n", String.format("%.2f", bestOffer.getDeliveryCost()));
        System.out.printf("[MobileBuyer] ║ Score   : %-32s║%n", String.format("%.4f", bestScore));
        System.out.println("[MobileBuyer] ╚══════════════════════════════════════════╝");
    }

    @Override
    public boolean done() {
        return done;
    }
}

// ----
// MobileBuyerAgent starts in MainContainer
//       │
//       ▼
// travels to Container1 → sends REQUEST → gets INFORM → saves Offer
//       │
//       ▼
// travels to Container2 → sends REQUEST → gets INFORM → saves Offer
//       │
//       ▼
// travels to Container3 → ... (for N sellers)
//       │
//       ▼
// travels BACK to MainContainer
//       → normalizes all offers
//       → computes f(x) for each
//       → announces winner
