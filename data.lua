-- Overrides condicionais de nome/descrição de protótipos.
--
-- Só é preciso mexer aqui quando o texto do jogo NÃO vem de uma chave de locale
-- (locale/pt-BR/*.cfg) — por exemplo, quando um protótipo usa `localised_name`
-- fixo definido pelo mod de origem, ou quando queremos um nome diferente
-- dependendo de quais mods estão ativos.
--
-- CONVENÇÃO (modelo autônomo + prioridade dos pacotes nativos, ver CLAUDE.md §3):
--   * Chaves de locale puras já são cópia fiel do texto do pacote nativo, então
--     a ordem de carga é irrelevante e NÃO precisam de guarda.
--   * Ao adicionar um override de protótipo de um mod dos ecossistemas
--     AAI / LTN / Bob's, proteja-o para o pacote nativo vencer quando ativo:
--         if not mods["AAI_Language_Pack"] then set_name(...) end
--         if not mods["LTN_Language_Pack"] then set_name(...) end
--         if not mods["boblocale"]        then set_name(...) end
--
-- Helpers com verificação de existência: se o protótipo não existir (mod
-- removido, renomeado ou substituído por uma total conversion), o override é
-- ignorado em vez de quebrar a carga.

local function proto(kind, name)
    local t = data.raw[kind]
    return t and t[name] or nil
end

local function set_name(kind, name, key)
    local p = proto(kind, name)
    if p then p.localised_name = key end
end

local function set_desc(kind, name, key)
    local p = proto(kind, name)
    if p then p.localised_description = key end
end

-- factorioplus: sem ele, damos nome/descrição próprios a alguns protótipos base.
if mods["factorioplus"] == nil then
    set_name("item", "rocket-fuel", {"item-name.slondo-ptbr-rocket-fuel"})
    set_desc("item", "rocket-fuel", {""})
    set_name("recipe", "rocket-fuel", {"recipe-name.slondo-ptbr-rocket-fuel"})
    set_name("technology", "rocket-fuel", {"technology-name.slondo-ptbr-rocket-fuel"})
    set_desc("technology", "rocket-fuel", {"technology-description.slondo-ptbr-rocket-fuel"})
    set_name("car", "car", {"entity-name.slondo-ptbr-car"})
end

-- space-age
if mods["space-age"] ~= nil then
    set_name("item", "tungsten-ore", {"item-name.slondo-ptbr-tungsten-ore"})
    set_desc("item", "tungsten-ore", {""})
    set_name("item", "tungsten-plate", {"item-name.slondo-ptbr-tungsten-plate"})
    set_name("autoplace-control", "tungsten_ore",
        {"autoplace-control-names.slondo-ptbr-tungsten-ore"})

    -- factorissimo 3
    if mods["factorissimo-2-notnotmelon"] == nil then
        set_desc("item", "agricultural-tower",
            {"entity-description.slondo-ptbr-agricultural-tower"})
    end
end

-- bioindustries2: sem ele, limpamos descrições herdadas de itens base.
if mods["Bio_Industries_2"] == nil then
    for _, name in ipairs({"wood", "coal", "solid-fuel"}) do
        set_desc("item", name, {""})
    end
end

-- canal-excavator sem pelagos
if mods["canal-excavator"] ~= nil and mods["pelagos"] == nil then
    set_name("technology", "canex-excavator",
        {"technology-name.slondo-ptbr-canex-excavator"})
    set_desc("technology", "canex-excavator",
        {"technology-description.slondo-ptbr-canex-excavator"})
    set_name("item", "canex-excavator", {"entity-name.slondo-ptbr-canex-excavator"})
    set_name("recipe", "canex-excavator", {"recipe-name.slondo-ptbr-canex-excavator"})
end

-- LargerLamps-2_0
if mods["LargerLamps-2_0"] == nil then
    set_name("item", "small-lamp", {"entity-name.slondo-ptbr-small-lamp"})
    set_desc("item", "small-lamp", {""})
end
