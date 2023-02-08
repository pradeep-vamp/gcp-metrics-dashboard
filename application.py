# dash components and basic libraries
from data.functions import debugmode
from main import app

application = app.server

import callbacks.authentication  # noqa: F401
import callbacks.campaign_lookup  # noqa: F401
import callbacks.financial  # noqa: F401
import callbacks.influencer_lookup  # noqa: F401
import callbacks.influencer_usage  # noqa: F401
import callbacks.overview  # noqa: F401
import callbacks.pandacop  # noqa: F401
import callbacks.platform_stats  # noqa: F401
import callbacks.pricing  # noqa: F401
import callbacks.segmentation  # noqa: F401
import callbacks.self_serve  # noqa: F401
import callbacks.talent  # noqa: F401

if __name__ == "__main__":
    application.run(debug=debugmode, port=8080, host="0.0.0.0")
