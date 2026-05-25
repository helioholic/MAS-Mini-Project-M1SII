package agents;

import jade.core.Agent;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import behaviours.BuyerBehaviour;
import utils.Constants;

public class BuyerAgent extends Agent {

    private double maxBudget;
    private String desiredProduct;

    @Override
    protected void setup() {
        desiredProduct = "Laptop";
        maxBudget = Math.random() * (1000 - 600) + 600; // random between 600-1000

        System.out.println("[Buyer] " + getLocalName() + " started");
        System.out.println("[Buyer] Desired product: " + desiredProduct);
        System.out.println("[Buyer] Max budget: " + String.format("%.2f", maxBudget));

        // Register in DF so seller can find buyers
        DFAgentDescription dfd = new DFAgentDescription();
        dfd.setName(getAID());
        ServiceDescription sd = new ServiceDescription();
        sd.setType(Constants.AUCTION_SERVICE);
        sd.setName("AuctionBuyer");
        dfd.addServices(sd);
        try {
            DFService.register(this, dfd);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        // Start listening for auction messages
        addBehaviour(new BuyerBehaviour(this));
    }

    public double getMaxBudget() {
        return maxBudget;
    }

    public String getDesiredProduct() {
        return desiredProduct;
    }

    @Override
    protected void takeDown() {
        try {
            DFService.deregister(this);
        } catch (FIPAException e) {
            e.printStackTrace();
        }
        System.out.println("[Buyer] " + getLocalName() + " shutting down.");
    }
}
