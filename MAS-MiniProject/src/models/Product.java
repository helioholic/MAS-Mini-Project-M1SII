package models;

public class Product {

    private String name;
    private double startingPrice;
    private double reservePrice;  // secret! only seller knows

    public Product(String name, double startingPrice, double reservePrice) {
        this.name = name;
        this.startingPrice = startingPrice;
        this.reservePrice = reservePrice;
    }

    public String getName() {
        return name;
    }

    public double getStartingPrice() {
        return startingPrice;
    }

    public double getReservePrice() {
        return reservePrice;
    }
}
