
-- event handler for UNIT_SPELLCAST_SUCCEEDED
function(unitID, spell, rank, lineID, spellID)
    -- 248812 = blowback
    -- 235271 = infusion
    if spellID == 248812 or spellID == 235271 then
        aura_env.update_timer = GetTime() + 1
    end
    return false
end

function()
    if aura_env.update_timer == nil or GetTime() < aura_env.update_timer then
        return false
    end
end