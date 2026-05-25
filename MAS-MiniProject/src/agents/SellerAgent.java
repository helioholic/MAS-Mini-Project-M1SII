package agents;

import jade.core.Agent;
import jade.core.AID;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import models.Product;
import behaviours.SellerBehaviour;

public class SellerAgent extends Agent {

    private Product product;
    private double currentPrice;

    protected void setup() {
        Object[] args = getArguments();
        if (args != null && args.length > 0) {
            product = (Product) args[0];
        } else {
            product = new Product("Laptop", 500.0, 800.0); // fallback
        }
        currentPrice = product.getStartingPrice();

        System.out.println("[Seller] Auction starting for: " + product.getName());
        System.out.println("[Seller] Starting price: " + currentPrice);
        System.out.println("[Seller] Reserve price is secret ;)");

        // 2. Register in the DF so buyers can find us if needed
        DFAgentDescription dfd = new DFAgentDescription();
        dfd.setName(getAID());
        ServiceDescription sd = new ServiceDescription();
        sd.setType(utils.Constants.SELLER_SERVICE);
        sd.setName("AuctionSeller");
        dfd.addServices(sd);
        try {
            DFService.register(this, dfd);
        } catch (FIPAException e) {
            e.printStackTrace();
        }

        // 3. Add the behaviour that runs the auction logic
        addBehaviour(new SellerBehaviour(this, product));
    }

    // Getters for the behaviour to use
    public double getCurrentPrice() {
        return currentPrice;
    }

    public void setCurrentPrice(double p) {
        currentPrice = p;
    }

    public Product getProduct() {
        return product;
    }

    @Override
    protected void takeDown() {
        // Unregister from DF when agent dies
        try {
            DFService.deregister(this);
        } catch (FIPAException e) {
            e.printStackTrace();
        }
        System.out.println("[Seller] Shutting down.");
    }
}

