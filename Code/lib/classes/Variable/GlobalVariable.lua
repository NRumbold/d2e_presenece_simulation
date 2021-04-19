GlobalVariable = {}
function GlobalVariable:new(globalVariableName, globalVariableConfig)

	local isGlobalVariableExists = function()
		return fibaro.getGlobalVariable(globalVariableName) ~= nil
	end

	local createGlobalVariable = function(globalVariableName, globalVariableConfig)
		if not isGlobalVariableExists(globalVariableName) then
			local logger = (function()
				if fibaro.QA ~= nil then
					return fibaro.QA.logger
				else
					return logger
				end
			end)()

			logger:warning("Global variable '" .. globalVariableName .. "' doesn't exists!")

			if globalVariableConfig == nil then
				logger:error("Global variable config not provided! Provide config to create GV automatically or create it manually!")
			else
				globalVariableConfig.value = tostring(globalVariableConfig.value)
				globalVariableConfig.values = (function()
					local stringValues = {}
					for _, value in pairs(globalVariableConfig.values) do
						table.insert(stringValues, tostring(value))
					end
					return stringValues
				end)()
			end

			logger:warning("Creating global variable '" .. globalVariableName .. "'...")
			logger:printTable(globalVariableName .. " config", globalVariableConfig)

			if not globalVariableConfig.isEnum then
				api.post("/globalVariables",
						{
							name = globalVariableConfig.name,
							value = tostring(globalVariableConfig.value)
						}
				)
				logger:trace("Global variable " .. globalVariableConfig.name .. " created. Value set to " .. globalVariableConfig.value)
			else
				api.post("/globalVariables",
						{
							name = globalVariableConfig.name,
						}
				)
				logger:trace("Global variable " .. globalVariableConfig.name .. " created")
			end
			if globalVariableConfig.isEnum then
				logger:trace("Setting the enum values...")
				api.put("/globalVariables/" .. globalVariableConfig.name,
						{
							name = globalVariableConfig.name,
							value = globalVariableConfig.values[1],
							isEnum = true,
							enumValues = globalVariableConfig.values
						}
				)
				logger:trace("Enum values set for " .. globalVariableConfig.name .. " Current value is " .. tostring(globalVariableConfig.values[1]))
			end
		end
	end

	createGlobalVariable(globalVariableName, globalVariableConfig)

	local this = {
		globalVariableName = globalVariableName,
		value = (function()
			local value = fibaro.getGlobalVariable(globalVariableName)
			if value == "true" then
				return true
			elseif value == "false" then
				return false
			elseif type(tonumber(value)) == "number" then
				return tonumber(value)
			elseif value == "nil" or value == nil then

				return nil
			else
				return value
			end
		end)(),
	}

	function this:getValue()
		return self.value
	end

	function this:getGlobalValue()
		local value = fibaro.getGlobalVariable(self.globalVariableName)

		if value == "true" then
			self.value = true
		elseif value == "false" then
			self.value = false
		elseif type(tonumber(value)) == "number" then
			self.value = tonumber(value)
		elseif self.value == "nil" then
			return nil
		else
			self.value = value
		end

		return self.value
	end

	function this:setValue(value)
		if value == "true" then
			self.value = true
		elseif value == "false" then
			self.value = false
		elseif type(tonumber(value)) == "number" then
			self.value = tonumber(value)
		else
			self.value = value
		end
	end

	function this:setGlobalValue(value)
		self:setValue(value)
		fibaro.setGlobalVariable(self.globalVariableName, tostring(value))
	end

	function this:saveValue()
		fibaro.setGlobalVariable(self.globalVariableName, tostring(self.value))
	end

	return this
end
