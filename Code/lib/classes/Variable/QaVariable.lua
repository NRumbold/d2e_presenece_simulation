QaVariable = {}
function QaVariable:new(variableName, initValue)
    local isVariableExists = function(variableName)
        local device = api.get("/devices/"..fibaro.QA.ID)
        for _, qaVariable in pairs(device.properties.quickAppVariables) do
            if qaVariable.name == variableName then return true end
        end
        return false
    end

    local createQaVariable = function(globalVariableName)
        if not isVariableExists(variableName) then
            local logger = (function()
                if fibaro.QA ~= nil then
                    return fibaro.QA.logger
                else
                    return logger
                end
            end)()

            logger:warning("QA variable '" .. variableName .. "' doesn't exists!")
            logger:warning("Creating QA variable '" .. variableName .. "'...")

            if initValue == nil then initValue = "" end

            local device = api.get("/devices/"..fibaro.QA.ID)
            local qaVariable = {
                name = variableName,
                value = initValue
            }
            table.insert(device.properties.quickAppVariables, qaVariable)
            api.put("/devices/"..fibaro.QA.ID, device)

            logger:trace("QA variable " .. variableName .. " created")
        end
    end

    createQaVariable(variableName)

    local this = {
        variableName = variableName
    }

    function this:getValue()
        local value = fibaro.QA:getVariable(variableName)
        if value == "true" then
            return true
        elseif value == "false" then
            return false
        elseif type(tonumber(value)) == "number" then
            return tonumber(value)
        elseif value == "nil" then
            return nil
        else
            return value
        end
    end

    function this:setValue(value)
        if value == "true" then
            value = true
        elseif value == "false" then
            value = false
        elseif type(tonumber(value)) == "number" then
            value = tonumber(value)
        else
            value = value
        end
        fibaro.QA:setVariable(self.variableName, value)
    end

    return this
end
