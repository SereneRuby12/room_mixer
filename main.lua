meta.name = "Room Mixer"
meta.description = "Mixes rooms from every level.\nDisable some of the options below in case of getting crashes while playing online."
meta.author = "SereneRuby12"
meta.version = "1.0a"

state = nil
---@cast state nil

local pre_floor_cb_id = -1

local NOTOP_TEMPLATES = {
    [ROOM_TEMPLATE.PATH_NOTOP] = true,
    [ROOM_TEMPLATE.PATH_DROP_NOTOP] = true,
    [ROOM_TEMPLATE.EXIT_NOTOP] = true,
    [ROOM_TEMPLATE.MACHINE_TALLROOM_PATH] = true,
    [ROOM_TEMPLATE.MACHINE_BIGROOM_PATH] = true,
    [ROOM_TEMPLATE.ANUBIS_ROOM] = true,
    [ROOM_TEMPLATE.MOAI] = true,
    [ROOM_TEMPLATE.TUSKFRONTDICESHOP_LEFT] = true,
    [ROOM_TEMPLATE.TUSKFRONTDICESHOP] = true,
    [ROOM_TEMPLATE.FEELING_TOMB] = true,
}

local FLOORS = {ENT_TYPE.FLOOR_GENERIC, ENT_TYPE.FLOOR_SURFACE, ENT_TYPE.FLOOR_JUNGLE, ENT_TYPE.FLOOR_TUNNEL_CURRENT, ENT_TYPE.FLOOR_TUNNEL_NEXT, ENT_TYPE.FLOOR_PEN, ENT_TYPE.FLOOR_TOMB, ENT_TYPE.FLOORSTYLED_BABYLON, ENT_TYPE.FLOORSTYLED_BEEHIVE, ENT_TYPE.FLOORSTYLED_COG, ENT_TYPE.FLOORSTYLED_DUAT, ENT_TYPE.FLOORSTYLED_GUTS, ENT_TYPE.FLOORSTYLED_MINEWOOD, ENT_TYPE.FLOORSTYLED_MOTHERSHIP, ENT_TYPE.FLOORSTYLED_PAGODA, ENT_TYPE.FLOORSTYLED_STONE, ENT_TYPE.FLOORSTYLED_SUNKEN, ENT_TYPE.FLOORSTYLED_TEMPLE, ENT_TYPE.FLOORSTYLED_VLAD}

local TEXTURE_BY_THEME = {
    [THEME.DWELLING] = TEXTURE.DATA_TEXTURES_FLOOR_CAVE_0,
    [THEME.JUNGLE] = TEXTURE.DATA_TEXTURES_FLOOR_JUNGLE_0,
    [THEME.VOLCANA] = TEXTURE.DATA_TEXTURES_FLOOR_VOLCANO_0,
    [THEME.OLMEC] = TEXTURE.DATA_TEXTURES_FLOOR_JUNGLE_0,
    [THEME.TIDE_POOL] = TEXTURE.DATA_TEXTURES_FLOOR_TIDEPOOL_0,
    [THEME.TEMPLE] = TEXTURE.DATA_TEXTURES_FLOOR_TEMPLE_0,
    [THEME.ICE_CAVES] = TEXTURE.DATA_TEXTURES_FLOOR_ICE_0,
    [THEME.NEO_BABYLON] = TEXTURE.DATA_TEXTURES_FLOOR_BABYLON_0,
    [THEME.SUNKEN_CITY] = TEXTURE.DATA_TEXTURES_FLOOR_SUNKEN_0,
    [THEME.HUNDUN] = TEXTURE.DATA_TEXTURES_FLOOR_SUNKEN_0
}
local TEXTURE_BY_SUBTHEME = {
    [COSUBTHEME.DWELLING] = TEXTURE.DATA_TEXTURES_FLOOR_CAVE_0,
    [COSUBTHEME.JUNGLE] = TEXTURE.DATA_TEXTURES_FLOOR_JUNGLE_0,
    [COSUBTHEME.VOLCANA] = TEXTURE.DATA_TEXTURES_FLOOR_VOLCANO_0,
    [COSUBTHEME.TIDE_POOL] = TEXTURE.DATA_TEXTURES_FLOOR_TIDEPOOL_0,
    [COSUBTHEME.TEMPLE] = TEXTURE.DATA_TEXTURES_FLOOR_TEMPLE_0,
    [COSUBTHEME.ICE_CAVES] = TEXTURE.DATA_TEXTURES_FLOOR_ICE_0,
    [COSUBTHEME.NEO_BABYLON] = TEXTURE.DATA_TEXTURES_FLOOR_BABYLON_0,
    [COSUBTHEME.SUNKEN_CITY] = TEXTURE.DATA_TEXTURES_FLOOR_SUNKEN_0,
}
local DEFAULT_TEXTURE = TEXTURE.DATA_TEXTURES_FLOOR_TEMPLE_0

local function get_theme_texture()
    local state = get_local_state()
    if state.theme == THEME.COSMIC_OCEAN then
        return TEXTURE_BY_SUBTHEME[get_co_subtheme()] or DEFAULT_TEXTURE
    else
        return TEXTURE_BY_THEME[state.theme] or DEFAULT_TEXTURE
    end
end

set_callback(function ()
    if options.grow_growables then
        grow_chainandblocks()
        grow_poles(LAYER.BOTH, 120)
        grow_vines(LAYER.BOTH, 120)
    end
    local state = get_local_state()
    if options.fix_spike_textures then
        local co_theme = get_co_subtheme()
        local is_co = co_theme > COSUBTHEME.NONE
        if state.theme ~= THEME.DWELLING or (is_co and co_theme ~= COSUBTHEME.DWELLING) then
            for _, spike_uid in ipairs(get_entities_by(ENT_TYPE.FLOOR_SPIKES, MASK.FLOOR, LAYER.BOTH)) do
                local spike = get_entity(spike_uid)
                if spike.animation_frame == 116 then
                    spike:set_texture(TEXTURE.DATA_TEXTURES_FLOOR_CAVE_0)
                end
            end
        end
        if state.theme ~= THEME.ICE_CAVES or (is_co and co_theme ~= COSUBTHEME.ICE_CAVES) then
            for _, spike_uid in ipairs(get_entities_by(ENT_TYPE.FLOOR_SPIKES_UPSIDEDOWN, MASK.FLOOR, LAYER.BOTH)) do
                local x, y, l = get_position(spike_uid)
                local floor_uid = get_grid_entity_at(x, y+1, l)
                if get_entity_type(floor_uid) ~= ENT_TYPE.FLOOR_ICE then
                    for _, deco_uid in ipairs(entity_get_items_by(floor_uid, ENT_TYPE.DECORATION_GENERIC, MASK.DECORATION)) do
                        local deco = get_entity(deco_uid)
                        if deco.animation_frame > 103 and deco.animation_frame < 107 then
                            deco:set_texture(get_theme_texture())
                            deco.animation_frame = deco.animation_frame - 3
                            deco.angle = math.pi
                            break
                        end
                    end
                    local spike = get_entity(spike_uid)
                    spike:set_texture(get_theme_texture())
                    spike.animation_frame = spike.animation_frame - 3
                    spike.angle = math.pi
                end
            end
        end
    end
    if options.fix_quicksand_deco then
        for _, uid in ipairs(get_entities_by(ENT_TYPE.FLOOR_QUICKSAND, MASK.FLOOR, LAYER.BOTH)) do
            for _, deco_uid in ipairs(entity_get_items_by(uid, ENT_TYPE.DECORATION_GENERIC, MASK.DECORATION)) do
                get_entity(deco_uid):set_texture(TEXTURE.DATA_TEXTURES_FLOOR_TEMPLE_0)
            end
        end
    end
end, ON.POST_LEVEL_GENERATION)

local spawned_floors = {}

--Functions used for preventing some blocked paths
local function hasnt_open_path_prev(x, y)
    if (x-3)%10 ~= 0 then
        x = x-1
        local first = x - ((x - 3) % 10)
        for lx=x, first, -1 do
            if not (spawned_floors[y][lx] or spawned_floors[y-1][lx]) then --get_grid_entity_at(lx, y, l) == -1 and get_grid_entity_at(lx, y-1, l) == -1 then
                return false
            end
        end
    end
    return true
end

local function hasnt_open_path_next(x, y)
    x = x+1
    local last = x + (10 - ((x - 2) % 10)) - 1
    for lx=x, last do
        if not spawned_floors[y][lx] then
            return false
        end
    end
    return true
end

local function pre_floor_callback(_, x, y, l)
    if l == LAYER.FRONT and y % 8 == 2 and not spawned_floors[y+1][x] then
        local template
        do
            local ix, iy = get_room_index(x, y)
            template = get_room_template(ix, iy, LAYER.FRONT)
        end
        if NOTOP_TEMPLATES[template] then
            if (x % 10 == 2 or hasnt_open_path_next(x, y+1)) and hasnt_open_path_prev(x, y+1) then
                return spawn_grid_entity(ENT_TYPE.FX_SHADOW, x, y, l)
            end
        end
    end
    spawned_floors[y][x] = true
end
--

set_callback(function ()
    if options.fix_path then
        local state = get_local_state()
        spawned_floors = {}
        for y = 122-state.height*8, 123 do
            spawned_floors[y] = {}
        end
        if pre_floor_cb_id == -1 then
            pre_floor_cb_id = set_pre_entity_spawn(pre_floor_callback, SPAWN_TYPE.LEVEL_GEN, MASK.FLOOR, FLOORS)
        end
    else
        clear_callback(pre_floor_cb_id)
        pre_floor_cb_id = -1
    end
end, ON.POST_ROOM_GENERATION)

register_option_bool("fix_path", "Fix blocked paths", "Won't fix every blocked path, only path_drop (the most common one)", true)
register_option_bool("grow_growables", "Grow growable entities", "Fixes vines, poles and chains not growing when not on the themes where they originally spawn", true)
register_option_bool("fix_spike_textures", "Fix spike textures", "Spikes on bones and upside down spikes have incorrect textures when out of their respective themes", true)
register_option_bool("fix_quicksand_deco", "Fix quicksand textures", "Won't fix the textures when one becomes destroyed, only on level gen", true)
