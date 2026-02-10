class SelfHealingAgent:
    def run_with_healing(self, command):
        try:
            subprocess.check_call(command)
            return True
        except subprocess.CalledProcessError as e:
            return self._heal(e, command)

    def _heal(self, error, command):
        msg = str(error)

        print("\n🩹 Self-Healing Activated")

        # Case 1: Model missing
        if "Model not found" in msg or "model.pkl" in msg:
            print("🔧 Healing: model missing → retrain required")
            return False

        # Case 2: Target missing
        if "Target column required" in msg:
            print("🔧 Healing: switching to recommendation mode")
            return False

        # Case 3: No numeric data
        if "No numeric features" in msg:
            print("❌ Cannot heal: dataset incompatible")
            return False

        print("❌ Unhandled error:", msg)
        return False
