package agents;

import jade.core.Agent;
import jade.domain.DFService;
import jade.domain.FIPAAgentManagement.DFAgentDescription;
import jade.domain.FIPAAgentManagement.ServiceDescription;
import jade.domain.FIPAException;
import behaviours.MobileBuyerBehaviour;
import utils.Constants;

import java.util.Arrays;

import java.util.List;

public class MobileBuyerAgent extends Agent {

    @Override
    protected void setup() {
        // Get seller names and container names from launcher
        Object[] args = getArguments();
        if (args == null || args.length < 2) {
            System.out.println("[MobileBuyer] No arguments provided. Shutting down.");
            doDelete();
            return;
        }

        // args[0] = comma-separated seller names   "SellerA,SellerB,SellerC"
        // args[1] = comma-separated container names "Container1,Container2,Container3"
        List<String> sellerNames = Arrays.asList(((String) args[0]).split(","));
        List<String> containerNames = Arrays.asList(((String) args[1]).split(","));

        System.out.println("[MobileBuyer] Starting in: " + here().getName());
        System.out.println("[MobileBuyer] Will visit sellers: " + sellerNames);
        System.out.println("[MobileBuyer] Preferences → Price: " + Constants.PREF_PRICE
                + " | Quality: " + Constants.PREF_QUALITY
                + " | Delivery: " + Constants.PREF_DELIVERY);

        addBehaviour(new MobileBuyerBehaviour(this, sellerNames, containerNames));
    }

    @Override
    protected void afterMove() {
        // Called automatically by JADE after every migration
        // We just log it — the behaviour resumes automatically
        System.out.println("[MobileBuyer] Arrived in container: " + here().getName());
    }

    @Override
    protected void takeDown() {
        System.out.println("[MobileBuyer] Shutting down in: " + here().getName());
    }
}

// One important method: afterMove()
// This is a JADE lifecycle callback, like setup() and takeDown(), but called automatically every time the agent finishes a migration. You can use it to re-register in the DF, reconnect to services, etc. We just log it for now.
// The full JADE agent lifecycle looks like this:
// setup()
//   │
//   ▼
// [normal execution + behaviours]
//   │
//   ├── doMove() called
//   │     ▼
//   │   beforeMove()  ← called before leaving (we didn't override this)
//   │     ▼
//   │   [agent migrates]
//   │     ▼
//   │   afterMove()   ← called after arriving ✓ we override this
//   │     ▼
//   │   [behaviours resume automatically]
//   │
//   └── doDelete() called
//         ▼
//       takeDown()
// Inter-container (same platform):
// ┌─────────────────────────────────┐
// │       JADE Platform             │
// │  ┌──────────┐  ┌──────────┐     │
// │  │Container1│  │Container2│     │
// │  │ Seller1  │  │ Seller2  │     │
// │  └──────────┘  └──────────┘     │
// │  ┌──────────┐                   │
// │  │  Main    │  ← buyer starts   │
// │  │Container │    here, travels  │ 
// │  └──────────┘    to each one    │ 
// └─────────────────────────────────┘
// Inter-platform (different platforms):
// ┌──────────────┐    ┌──────────────┐
// │  Platform 1  │    │  Platform 2  │
// │  port 1099   │    │  port 1100   │
// │  Seller1     │    │  Seller2     │
// └──────────────┘    └──────────────┘
//      ↑ buyer travels between platforms

