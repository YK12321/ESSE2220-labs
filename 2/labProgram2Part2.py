import space_controller
import random
import time
import threading
import logging
import signal
import sys

# Configure logging for the main application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for simulation control
simulation_running = True
battery_lock = threading.Lock()
ledDisplayObject = None

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    global simulation_running
    logger.info("Received interrupt signal, stopping simulation...")
    simulation_running = False

def battery_discharge_simulation():
    """Simulate battery discharge with random tick speed"""
    global simulation_running
    current_battery = 100
    
    logger.info("Starting battery discharge simulation...")
    logger.info("Press Ctrl+C to stop the simulation")
    
    while simulation_running and current_battery > 0:
        try:
            # Random tick speed between 0.5 and 3 seconds
            random_tick_speed = random.uniform(0.5, 3.0)
            
            # Random battery decrease between 1-5%
            battery_decrease = random.randint(1, 5)
            
            # Update battery level with thread safety
            with battery_lock:
                current_battery = max(0, current_battery - battery_decrease)
                ledDisplayObject.setBatteryLevel(current_battery)
            
            logger.info(f"Tick speed: {random_tick_speed:.2f}s | Battery decreased by {battery_decrease}%")
            ledDisplayObject.updateLedStates()
            logger.info("-" * 50)
            
            # Wait for random tick speed
            time.sleep(random_tick_speed)
            
        except space_controller.LEDDisplayError as e:
            logger.error(f"LED Display error: {e}")
            break
        except Exception as e:
            logger.error(f"Unexpected error in battery simulation: {e}")
            break
    
    logger.info("Battery simulation completed!")

def main():
    """Main function to run the battery simulation"""
    global simulation_running, ledDisplayObject
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Initialize LED display with context manager for automatic cleanup
        with space_controller.LEDDisplay(
            batteryInput=100, 
            ledPinsArrStatus=[0]*10, 
            ledPinsArr=[4, 5, 6, 12, 13, 16, 17, 18, 19, 20]
        ) as ledDisplayObject:
            
            logger.info("LED Display initialized successfully")
            
            # Initialize LED states
            ledDisplayObject.calculateLedStates()
            ledDisplayObject.updateLedStates()
            logger.info("Initial state set")
            logger.info("-" * 50)
            
            # Start battery discharge simulation in a separate thread
            battery_thread = threading.Thread(target=battery_discharge_simulation)
            battery_thread.daemon = True
            battery_thread.start()
            
            # Keep main thread alive
            while simulation_running and battery_thread.is_alive():
                time.sleep(0.1)
            
            # Wait for thread to finish
            if battery_thread.is_alive():
                logger.info("Waiting for simulation thread to finish...")
                battery_thread.join(timeout=5.0)
            
            # Print final status
            final_status = ledDisplayObject.get_status()
            logger.info(f"Final status: {final_status}")
            
    except space_controller.LEDDisplayError as e:
        logger.error(f"LED Display initialization failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
    finally:
        logger.info("Simulation ended")

if __name__ == "__main__":
    main()
