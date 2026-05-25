package behaviours;

import jade.core.AID;
import jade.core.behaviours.Behaviour;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;
import agents.SellerAgent;
import models.Product;
import utils.Constants;

import java.util.ArrayList;
import java.util.List;

public class SellerBehaviour extends Behaviour {

    private SellerAgent seller;
    private Product product;
    private List<AID> buyers;
    private int phase = 0;
    private boolean done = false;
    private long roundStartTime = 0;

    private AID bestBidder = null;
    private double bestBid = 0;
    private int repliesReceived = 0;
    private AID overallWinner = null;
    private double overallBestPrice = 0;

    private String convId = "auction-" + System.currentTimeMillis();

    public SellerBehaviour(SellerAgent seller, Product product) {
        super(seller);
        this.seller = seller;
        this.product = product;
        this.buyers = new ArrayList<>();
    }

    @Override
    public void action() {

        // ── PHASE 0: Find all buyers in DF ──────────────────────────
        if (phase == 0) {
            System.out.println("[Seller] Searching for buyers...");
            DFAgentDescription template = new DFAgentDescription();
            ServiceDescription sd = new ServiceDescription();
            sd.setType(Constants.AUCTION_SERVICE);
            template.addServices(sd);

            try {
                DFAgentDescription[] results = DFService.search(seller, template);
                for (DFAgentDescription dfd : results) {
                    buyers.add(dfd.getName());
                }
                System.out.println("[Seller] Found " + buyers.size() + " buyer(s).");
            } catch (FIPAException e) {
                e.printStackTrace();
            }

            if (buyers.isEmpty()) {
                System.out.println("[Seller] No buyers found. Ending auction.");
                done = true;
                return;
            }
            phase = 1;
        } // ── PHASE 1: Send CFP to all buyers ─────────────────────────
        else if (phase == 1) {
            System.out.println("\n[Seller] ══════════════════════════════════");
            System.out.println("[Seller]  ROUND | Current Price: " + String.format("%.2f", seller.getCurrentPrice()));
            System.out.println("[Seller] ══════════════════════════════════");

            ACLMessage cfp = new ACLMessage(ACLMessage.CFP);
            cfp.setContent(product.getName() + ":" + seller.getCurrentPrice());
            cfp.setConversationId(convId);
            for (AID buyer : buyers) {
                cfp.addReceiver(buyer);
            }
            seller.send(cfp);

            bestBidder = null;
            bestBid = 0;
            repliesReceived = 0;
            phase = 2;
        } // ── PHASE 2: Collect bids ────────────────────────────────────
        else if (phase == 2) {
            if (roundStartTime == 0) {
                roundStartTime = System.currentTimeMillis();
            }

            MessageTemplate mt = MessageTemplate.and(
                    MessageTemplate.MatchConversationId(convId),
                    MessageTemplate.MatchPerformative(ACLMessage.PROPOSE)
            );

            ACLMessage reply = seller.receive(mt);

            if (reply != null) {
                double bidAmount = Double.parseDouble(reply.getContent());
                repliesReceived++;
                System.out.println("[Seller] ✓ Bid from " + reply.getSender().getLocalName()
                        + ": " + String.format("%.2f", bidAmount));

                if (bidAmount > bestBid) {
                    bestBid = bidAmount;
                    bestBidder = reply.getSender();
                }

                if (repliesReceived >= buyers.size()) {
                    roundStartTime = 0;
                    phase = 3;
                }
            } else {
                long elapsed = System.currentTimeMillis() - roundStartTime;
                if (elapsed >= Constants.BID_WAIT_TIME) {
                    System.out.println("[Seller] Wait time expired. Bids received: "
                            + repliesReceived + "/" + buyers.size());
                    roundStartTime = 0;
                    phase = 3;
                } else {
                    block(Constants.BID_WAIT_TIME - elapsed);
                }
            }
        } // ── PHASE 3: Process round results ───────────────────────────
        else if (phase == 3) {
            if (bestBidder == null) {
                endAuction();
            } else {
                seller.setCurrentPrice(bestBid);
                overallWinner = bestBidder;
                overallBestPrice = bestBid;
                System.out.println("[Seller] ★ Best bid: " + bestBidder.getLocalName()
                        + " → " + String.format("%.2f", bestBid));

                ACLMessage inform = new ACLMessage(ACLMessage.INFORM);
                inform.setContent("HIGHEST:" + bestBid);
                inform.setConversationId(convId);
                for (AID buyer : buyers) {
                    inform.addReceiver(buyer);
                }
                seller.send(inform);
                phase = 1;
            }
        }
    }

    // ── End auction & announce result ────────────────────────────────
    private void endAuction() {
        System.out.println("\n[Seller] ╔══════════════════════════════════╗");
        System.out.println("[Seller] ║         AUCTION RESULT           ║");
        System.out.println("[Seller] ╠══════════════════════════════════╣");
        System.out.println("[Seller] ║ Item   : " + String.format("%-24s", product.getName()) + "║");
        System.out.println("[Seller] ║ Final  : " + String.format("%-24s", String.format("%.2f", seller.getCurrentPrice())) + "║");
        System.out.println("[Seller] ║ Reserve: " + String.format("%-24s", String.format("%.2f", product.getReservePrice())) + "║");

        if (overallWinner != null && overallBestPrice >= product.getReservePrice()) {
            System.out.println("[Seller] ║ Winner : " + String.format("%-24s", overallWinner.getLocalName()) + "║");
            System.out.println("[Seller] ║ Status : ✓ SOLD                  ║");
            System.out.println("[Seller] ╚══════════════════════════════════╝");

            ACLMessage accept = new ACLMessage(ACLMessage.ACCEPT_PROPOSAL);
            accept.addReceiver(overallWinner);
            accept.setContent("SOLD:" + seller.getCurrentPrice());
            accept.setConversationId(convId);
            seller.send(accept);

            for (AID buyer : buyers) {
                if (!buyer.equals(overallWinner)) {
                    ACLMessage reject = new ACLMessage(ACLMessage.REJECT_PROPOSAL);
                    reject.addReceiver(buyer);
                    reject.setContent("AUCTION_OVER");
                    reject.setConversationId(convId);
                    seller.send(reject);
                }
            }
        } else {
            System.out.println("[Seller] ║ Status : ✗ RESERVE NOT MET       ║");
            System.out.println("[Seller] ╚══════════════════════════════════╝");

            ACLMessage inform = new ACLMessage(ACLMessage.INFORM);
            inform.setContent("AUCTION_OVER:RESERVE_NOT_MET");
            inform.setConversationId(convId);
            for (AID buyer : buyers) {
                inform.addReceiver(buyer);
            }
            seller.send(inform);
        }

        done = true;
        seller.doDelete();
    }

    @Override
    public boolean done() {
        return done;
    }
}
