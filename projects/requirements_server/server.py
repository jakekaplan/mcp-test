import pandas as pd

import logging
import time
from datetime import datetime

from fastmcp import FastMCP

from helpers import TEST_VALUE, get_message
from utils.nested import NESTED_CONSTANT, nested_function

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Requirements Test Server")

# Log fancy startup banner
logger.info("")
logger.info("╔══════════════════════════════════════════════╗")
logger.info("║   📦 REQUIREMENTS TEST SERVER STARTING 📦    ║")
logger.info("╠══════════════════════════════════════════════╣")
logger.info("║   🚀 Testing pandas from requirements.txt    ║")
logger.info("║   ⏰ Started: %-30s ║" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
logger.info("╚══════════════════════════════════════════════╝")
logger.info("")


@mcp.tool
def test_tool() -> str:
    """Tests imports and pandas functionality."""
    start_time = time.time()

    # Log request
    logger.info("┌──────────────────────────────────────┐")
    logger.info("│ 🧪 TEST TOOL INVOKED                 │")
    logger.info("├──────────────────────────────────────┤")
    logger.info("│ Testing all imports...               │")
    logger.info("└──────────────────────────────────────┘")

    # Test imports
    logger.info(f"✓ Top-level import: {TEST_VALUE}")
    logger.info(f"✓ Top-level function: {get_message()}")
    logger.info(f"✓ Nested constant: {NESTED_CONSTANT}")
    logger.info(f"✓ Nested function: {nested_function()}")

    # Create sample DataFrame
    data = {
        'ID': [1, 2, 3],
        'Value': [10, 20, 30],
        'Nested': [NESTED_CONSTANT] * 3
    }

    df = pd.DataFrame(data)

    # Convert to string
    result = f"All imports successful!\n\nDataFrame:\n{df.to_string()}"

    # Log result
    elapsed_ms = (time.time() - start_time) * 1000
    logger.info("✅ Test completed in %.2fms" % elapsed_ms)
    logger.info("")

    return result


if __name__ == "__main__":
    logger.info("🌟 Server ready and listening...")
    logger.info("💡 Available tools: test_tool")
    logger.info("")
    mcp.run()
