package agents;

import jade.core.Agent;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import jade.lang.acl.ACLMessage;
import jade.lang.acl.MessageTemplate;
import jade.core.behaviours.CyclicBehaviour;
import utils.Constants;

public class SellerAgent2 extends Agent {

    // This seller's offer values (hardcoded per seller, set via arguments)
    private double price;
    private double quality;
    private double deliveryCost;

    @Override
    protected void setup() {
        // Get offer values passed from launcher
        Object[] args = getArguments();
        if (args != null && args.length == 3) {
            price = (double) args[0];
            quality = (double) args[1];
            deliveryCost = (double) args[2];
        } else {
            // fallback defaults
            price = 500.0;
            quality = 7.0;
            deliveryCost = 30.0;
        }

        System.out.println("[Seller2] " + getLocalName() + " ready in "
                + here().getName()); // here() returns current container
        System.out.printf("[Seller2] Offer → Price: %.2f | Quality: %.2f | Delivery: %.2f%n",
                price, quality, deliveryCost);

        // Register in DF
        DFAgentDescription dfd = new DFAgentDescription();
        dfd.setName(getAID());
        ServiceDescription sd = new ServiceDescription();
        sd.setType(Constants.SELLER2_SERVICE);
        sd.setName(getLocalName());
        dfd.addServices(sd);
        try {
            DFService.register(this, dfd);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        // Wait for buyer to arrive and request offer
        addBehaviour(new CyclicBehaviour(this) {
            @Override
            public void action() {
                MessageTemplate mt = MessageTemplate.MatchPerformative(ACLMessage.REQUEST);
                ACLMessage msg = myAgent.receive(mt);

                if (msg != null) {
                    System.out.println("[Seller2] " + getLocalName()
                            + " received offer request from " + msg.getSender().getLocalName());

                    // Reply with offer: "price:quality:deliveryCost"
                    ACLMessage reply = msg.createReply();
                    reply.setPerformative(ACLMessage.INFORM);
                    reply.setContent(price + ":" + quality + ":" + deliveryCost);
                    myAgent.send(reply);

                    System.out.println("[Seller2] " + getLocalName() + " sent offer.");
                } else {
                    block();
                }
            }
        });
    }

    @Override
    protected void takeDown() {
        try {
            DFService.deregister(this);
        } catch (FIPAException e) {
            e.printStackTrace();
        }
        System.out.println("[Seller2] " + getLocalName() + " shutting down.");
    }
}

// SellerAgent2 starts
//       │
//       ├── prints its offer values (price, quality, delivery)
//       ├── registers in DF as "seller2"
//       └── adds CyclicBehaviour → just WAITS
//            (buyer agent travels to this container)
// CyclicBehaviour wakes up when a REQUEST arrives
//       │
//       ├── reads the REQUEST message
//       ├── creates a reply (INFORM) with "price:quality:deliveryCost"
//       └── sends it back to whoever asked
//            → then goes back to waiting
