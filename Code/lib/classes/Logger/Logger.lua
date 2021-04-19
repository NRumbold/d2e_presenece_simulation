Logger = {}
function Logger:new(tag)
    local this = {
        tag = tag,
        possibleLevels = {
            error = true,
            warning = true,
            trace = true,
            debug = true
        }
    }

    function this:log(level, message, tag)
        local currentLevel
        local currentTag = (function()
            if tag ~= nil then
                return tag
            else
                return self.tag
            end
        end)()

        if self.possibleLevels[level] ~= nil then
            currentLevel = level
        else
            currentLevel = "debug"
        end

        if currentLevel == "error" then
            fibaro.error(currentTag, message)
        elseif currentLevel == 'warning' then
            fibaro.warning(currentTag, message)
        elseif currentLevel == 'trace' then
            fibaro.trace(currentTag, message)
        else
            fibaro.debug(currentTag, message)
        end
    end

    function this:error(message, tag)
        self:log("error", message, tag)
    end

    function this:warning(message, tag)
        self:log("warning", message, tag)
    end

    function this:trace(message, tag)
        self:log("trace", message, tag)
    end

    function this:debug(message, tag)
        self:log("debug", message, tag)
    end

    function this:printTable(label, ...) -- add formatting print function that does auto-json on tables.
        local args = { ... }
        for i = 1, #args do local a = args[i]; args[i] = type(a) == 'table' and json.encode(a) or tostring(a) end
        self:debug(string.format(label..": %s", table.unpack(args)))
    end

    return this
end
