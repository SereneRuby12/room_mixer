meta.name = "Room Mixer"
meta.description = "Mixes rooms from every level"
meta.author = "Estebanfer"
meta.version = "1.0"

local CHAIN_THEMES = {
    [THEME.VOLCANA] = true,
    [THEME.CITY_OF_GOLD] = true,
    [THEME.DUAT] = true
}

local VINE_THEMES = {
    [THEME.JUNGLE] = true,
    [THEME.EGGPLANT_WORLD] = true
}

local POLE_THEMES = {
    [THEME.ABZU] = true,
    [THEME.EGGPLANT_WORLD] = true, --?
    [THEME.TIDE_POOL] = true
}

set_callback(function ()
    local co_theme = get_co_subtheme()
    if co_theme ~= COSUBTHEME.NONE then
        if co_theme ~= COSUBTHEME.JUNGLE then
            --grow_vines(LAYER.FRONT, 120)
        end
        if co_theme ~= COSUBTHEME.VOLCANA then
            grow_chainandblocks()
        end
        if co_theme ~= COSUBTHEME.TIDE_POOL then
            grow_poles(LAYER.FRONT, 120, AABB:new(get_bounds()), false)
        end
    else
        if not VINE_THEMES[state.theme] then
            --grow_vines(LAYER.FRONT, 120)
        end
        if not CHAIN_THEMES[state.theme] then
            grow_chainandblocks()
        end
        if not POLE_THEMES[state.theme] then
            grow_poles(LAYER.FRONT, 120, AABB:new(get_bounds()), false)
        end
    end
end, ON.POST_LEVEL_GENERATION)
