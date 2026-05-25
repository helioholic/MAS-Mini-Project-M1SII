package models;

public class Bid {

    private String buyerName;
    private double amount;

    public Bid(String buyerName, double amount) {
        this.buyerName = buyerName;
        this.amount = amount;
    }

    public String getBuyerName() {
        return buyerName;
    }

    public double getAmount() {
        return amount;
    }
}
