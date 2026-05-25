// wait for CFP  → decide bid → send PROPOSE (or stay silent)
// wait for result → HIGHEST: update price, new round
//               → SOLD: we won!
//               → AUCTION_OVER: auction ended
//               → REJECT: we lost
package behaviours;

import jade.core.behaviours.CyclicBehaviour;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;
import agents.BuyerAgent;

public class BuyerBehaviour extends CyclicBehaviour {

    private BuyerAgent buyer;
    private boolean active = true; // still participating in auction?
    private double currentAuctionPrice = 0;

    public BuyerBehaviour(BuyerAgent buyer) {
        super(buyer);
        this.buyer = buyer;
    }

    @Override
    public void action() {
        if (!active) {
            return; // dropped out, ignore all messages
        }
        // Listen for ANY relevant message
        ACLMessage msg = buyer.receive();

        if (msg == null) {
            block(); // nothing in inbox → sleep until message arrives
            return;
        }

        // ── CFP: seller asking for bids ──────────────────────────────
        if (msg.getPerformative() == ACLMessage.CFP) {
            String[] parts = msg.getContent().split(":");
            String productName = parts[0];
            currentAuctionPrice = Double.parseDouble(parts[1]);

            System.out.println("[Buyer-" + buyer.getLocalName().replace("Buyer", "") + "] CFP received → price: " + String.format("%.2f", currentAuctionPrice));

            // Only bid if this is our desired product AND price is under budget
            if (productName.equals(buyer.getDesiredProduct())
                    && currentAuctionPrice < buyer.getMaxBudget()) {

                // Bid: current price + random increment between 10 and 50
                double increment = 10 + Math.random() * 40;
                double myBid = currentAuctionPrice + increment;

                // But never bid more than our max budget
                if (myBid > buyer.getMaxBudget()) {
                    myBid = buyer.getMaxBudget();
                }

                ACLMessage propose = new ACLMessage(ACLMessage.PROPOSE);
                propose.addReceiver(msg.getSender()); // reply to seller
                propose.setContent(String.valueOf(myBid));
                propose.setConversationId(msg.getConversationId());
                buyer.send(propose);

                System.out.println("[Buyer-" + buyer.getLocalName().replace("Buyer", "") + "] CFP received → price: " + String.format("%.2f", currentAuctionPrice));

            } else {
                // Price too high or wrong product → drop out silently
                System.out.println("[Buyer-" + buyer.getLocalName().replace("Buyer", "") + "] ✗ Price too high (budget: " + String.format("%.2f", buyer.getMaxBudget()) + ")");

            }
        } // ── INFORM: seller broadcasting highest bid or auction over ──
        else if (msg.getPerformative() == ACLMessage.INFORM) {
            String content = msg.getContent();

            if (content.startsWith("HIGHEST:")) {
                double highestBid = Double.parseDouble(content.split(":")[1]);
                System.out.println("[Buyer-" + buyer.getLocalName().replace("Buyer", "") + "] Highest bid now: " + String.format("%.2f", highestBid));

            } else if (content.startsWith("AUCTION_OVER")) {
                System.out.println("[Buyer-" + buyer.getLocalName().replace("Buyer", "") + "] Auction ended. Reserve not met.");
                active = false;
                buyer.doDelete();
            }
        } // ── ACCEPT: we won! ──────────────────────────────────────────
        else if (msg.getPerformative() == ACLMessage.ACCEPT_PROPOSAL) {
            String price = msg.getContent().split(":")[1];
            System.out.println("[Buyer-" + buyer.getLocalName().replace("Buyer", "") + "] ★ WON the auction for: " + price);

            active = false;
            buyer.doDelete();
        } // ── REJECT: we lost ──────────────────────────────────────────
        else if (msg.getPerformative() == ACLMessage.REJECT_PROPOSAL) {
            System.out.println("[Buyer-" + buyer.getLocalName().replace("Buyer", "") + "] ✗ Lost the auction.");

            active = false;
            buyer.doDelete();
        }
    }
}
