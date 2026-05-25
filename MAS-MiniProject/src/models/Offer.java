package models;

import java.io.Serializable;

public class Offer implements Serializable {

    private String sellerName;
    private double price;
    private double quality;
    private double deliveryCost;

    public Offer(String sellerName, double price, double quality, double deliveryCost) {
        this.sellerName = sellerName;
        this.price = price;
        this.quality = quality;
        this.deliveryCost = deliveryCost;
    }

    public String getSellerName() {
        return sellerName;
    }

    public double getPrice() {
        return price;
    }

    public double getQuality() {
        return quality;
    }

    public double getDeliveryCost() {
        return deliveryCost;
    }

    @Override
    public String toString() {
        return String.format("[%s] Price=%.2f | Quality=%.2f | Delivery=%.2f",
                sellerName, price, quality, deliveryCost);
    }
}
