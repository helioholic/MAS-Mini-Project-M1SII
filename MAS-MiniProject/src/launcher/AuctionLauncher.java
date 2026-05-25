package launcher;

import jade.core.Profile;
import jade.core.ProfileImpl;
import jade.core.Runtime;
import jade.wrapper.AgentContainer;
import jade.wrapper.AgentController;
import jade.wrapper.StaleProxyException;
import models.Product;

import java.util.Scanner;

public class AuctionLauncher {

    static Scanner scanner = new Scanner(System.in);
    static AgentContainer container = null;

    public static void main(String[] args) {
        printBanner();
        boolean running = true;
        while (running) {
            printMainMenu();
            int choice = readInt();
            switch (choice) {
                case 1 ->
                    runPart1Menu();
                case 2 ->
                    runPart2();
                case 3 ->
                    System.out.println("  [Part 3] Coming soon...");
                case 4 ->
                    System.out.println("  [Part 4] Coming soon...");
                case 0 -> {
                    System.out.println("  Goodbye!");
                    running = false;
                }
                default ->
                    System.out.println("  Invalid choice.");
            }
        }
        scanner.close();
    }

    // ── Main Menu ────────────────────────────────────────────────────
    static void printMainMenu() {
        System.out.println("\n╔══════════════════════════════════════╗");
        System.out.println("║       MAS Mini-Project Menu          ║");
        System.out.println("╠══════════════════════════════════════╣");
        System.out.println("║  1. Part 1 - Auction                 ║");
        System.out.println("║  2. Part 2 - Mobile Agents           ║");
        System.out.println("║  3. Part 3 - AIMA Planning           ║");
        System.out.println("║  4. Part 4 - Multi-Agent Planning    ║");
        System.out.println("║  0. Exit                             ║");
        System.out.println("╚══════════════════════════════════════╝");
        System.out.print("Choice: ");
    }

    // ── Part 1 Sub-Menu ──────────────────────────────────────────────
    static void runPart1Menu() {
        System.out.println("\n╔══════════════════════════════════════╗");
        System.out.println("║         Part 1 - Auction             ║");
        System.out.println("╠══════════════════════════════════════╣");
        System.out.println("║  1. Quick test (random budgets)      ║");
        System.out.println("║  2. Custom setup                     ║");
        System.out.println("║  0. Back                             ║");
        System.out.println("╚══════════════════════════════════════╝");
        System.out.print("Choice: ");
        int choice = readInt();
        switch (choice) {
            case 1 ->
                runQuickAuction();
            case 2 ->
                runCustomAuction();
            case 0 -> {
                return;
            }
            default ->
                System.out.println("  Invalid choice.");
        }
    }

    // ── Quick Test: random budgets, default product ──────────────────
    static void runQuickAuction() {
        System.out.println("\n  [Quick Test] Launching with default product...");
        System.out.print("  Number of buyers (min 2): ");
        int numBuyers = readInt();
        if (numBuyers < 2) {
            numBuyers = 2;
        }
        Product product = new Product("Laptop", 500.0, 800.0);
        launchAuction(product, numBuyers);
    }

    // ── Custom Setup: user enters everything ─────────────────────────
    static void runCustomAuction() {
        System.out.println("\n  [Custom Setup]");
        scanner.nextLine(); // flush
        System.out.print("  Product name: ");
        String name = scanner.nextLine();
        System.out.print("  Starting price: ");
        double startPrice = scanner.nextDouble();
        System.out.print("  Reserve price: ");
        double reservePrice = scanner.nextDouble();
        System.out.print("  Number of buyers (min 2): ");
        int numBuyers = readInt();
        if (numBuyers < 2) {
            numBuyers = 2;
        }
        Product product = new Product(name, startPrice, reservePrice);
        launchAuction(product, numBuyers);
    }

    // ── Core launcher ────────────────────────────────────────────────
    static void launchAuction(Product product, int numBuyers) {
        try {
            Runtime rt = Runtime.instance();
            Profile profile = new ProfileImpl();
            profile.setParameter(Profile.GUI, "true");
            container = rt.createMainContainer(profile);

            // Launch buyers first
            for (int i = 1; i <= numBuyers; i++) {
                AgentController buyer = container.createNewAgent(
                        "Buyer" + i, "agents.BuyerAgent", null);
                buyer.start();
            }

            Thread.sleep(1000); // wait for buyers to register in DF

            // Launch seller
            AgentController seller = container.createNewAgent(
                    "Seller", "agents.SellerAgent", new Object[]{product});
            seller.start();

        } catch (StaleProxyException e) {
            System.err.println("Error creating agent: " + e.getMessage());
        } catch (InterruptedException e) {
            System.err.println("Interrupted: " + e.getMessage());
        }
    }

    // ── Part 2: Mobile Agents ────────────────────────────────────────
    static void runPart2() {
        System.out.println("\n╔══════════════════════════════════════╗");
        System.out.println("║     Part 2 - Mobile Agents           ║");
        System.out.println("╠══════════════════════════════════════╣");
        System.out.println("║  Inter-container negotiation         ║");
        System.out.println("║  1 buyer visits N sellers            ║");
        System.out.println("╚══════════════════════════════════════╝");

        try {
            // ── Step 1: Create JADE runtime ──────────────────────────
            Runtime rt = Runtime.instance();
            Profile mainProfile = new ProfileImpl();
            mainProfile.setParameter(Profile.GUI, "true");
            AgentContainer mainContainer = rt.createMainContainer(mainProfile);

            // ── Step 2: Create seller containers ─────────────────────
            // Each seller lives in its own container
            Profile p1 = new ProfileImpl();
            p1.setParameter(Profile.CONTAINER_NAME, "Container1");
            AgentContainer container1 = rt.createAgentContainer(p1);

            Profile p2 = new ProfileImpl();
            p2.setParameter(Profile.CONTAINER_NAME, "Container2");
            AgentContainer container2 = rt.createAgentContainer(p2);

            Profile p3 = new ProfileImpl();
            p3.setParameter(Profile.CONTAINER_NAME, "Container3");
            AgentContainer container3 = rt.createAgentContainer(p3);

            // ── Step 3: Launch seller agents in their containers ──────
            // SellerA: expensive, high quality, cheap delivery
            AgentController sellerA = container1.createNewAgent(
                    "SellerA", "agents.SellerAgent2",
                    new Object[]{600.0, 9.0, 20.0});
            sellerA.start();

            // SellerB: cheap, medium quality, expensive delivery
            AgentController sellerB = container2.createNewAgent(
                    "SellerB", "agents.SellerAgent2",
                    new Object[]{400.0, 6.0, 50.0});
            sellerB.start();

            // SellerC: medium price, medium quality, medium delivery
            AgentController sellerC = container3.createNewAgent(
                    "SellerC", "agents.SellerAgent2",
                    new Object[]{500.0, 7.0, 35.0});
            sellerC.start();

            Thread.sleep(1000); // wait for sellers to register

            // ── Step 4: Launch mobile buyer in main container ─────────
            AgentController mobileBuyer = mainContainer.createNewAgent(
                    "MobileBuyer",
                    "agents.MobileBuyerAgent",
                    new Object[]{
                        "SellerA,SellerB,SellerC", // seller names
                        "Container1,Container2,Container3" // their containers
                    });
            mobileBuyer.start();

        } catch (Exception e) {
            System.err.println("Error launching Part 2: " + e.getMessage());
        }
    }

    // ── Helpers ──────────────────────────────────────────────────────
    static void printBanner() {
        System.out.println("╔══════════════════════════════════════╗");
        System.out.println("║     MAS Mini-Project 2025-2026       ║");
        System.out.println("║     USTHB - M1 SII - Agents Tech     ║");
        System.out.println("╚══════════════════════════════════════╝");
    }

    static int readInt() {
        try {
            int val = scanner.nextInt();
            return val;
        } catch (Exception e) {
            scanner.nextLine(); // flush bad input
            return -1;
        }
    }
}
