Part 1 : 
javac -cp ".;../lib/jade.jar" models/*.java utils/*.java agents/BuyerAgent.java agents/SellerAgent.java behaviours/SellerBehaviour.java behaviours/BuyerBehaviour.java launcher/AuctionLauncher.java
java -cp ".;../lib/jade.jar" launcher.AuctionLauncher

Part 2 : 
javac -cp ".;../lib/jade.jar" models/*.java utils/*.java agents/BuyerAgent.java agents/SellerAgent.java agents/SellerAgent2.java agents/MobileBuyerAgent.java behaviours/SellerBehaviour.java behaviours/BuyerBehaviour.java behaviours/MobileBuyerBehaviour.java launcher/AuctionLauncher.java
java -cp ".;../lib/jade.jar" launcher.AuctionLauncher




