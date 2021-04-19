-- ************ BEGIN configuration block ************
LOGGER_TAG = "Test_Scene"
-- ************ END configuration block ************

-- ************ BEGIN creating classes ************
--#import("lib/classes/Variable/GlobalVariable.lua")
--#import("lib/classes/Logger/Logger.lua")
-- ************ END creating classes ************

-- ************ BEGIN creating objects************
logger = Logger:new(LOGGER_TAG)
-- ************ END creating objects ************

-- ************ BEGIN helper functions ************
-- ************ END helper functions ************

-- ************ BEGIN code block ************
logger:debug("START script")

logger:debug("END script")
-- ************ END code block ************