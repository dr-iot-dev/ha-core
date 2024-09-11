"""Creating a translation dictionary."""

# 日本語からエンティティ名への変換辞書
ja_to_entity_translation_dict = {
    "購入電気量": "electricity_purchased",
    "CO2削減量": "co2_reduction",
    "CO2排出量": "co2_emissions",
    "ガス消費量": "gas_consumption",
    "太陽光発電量": "solar_power_energy",
    "売電量": "electricity_sales",
    " 太陽光": "solar_panel",
    "１階トイレ コンセント": "1f_toilet_outlets",
    "キッチン 照明＆コンセント": "kitchen_lighting_and_outlets",
    "キッチン 食器洗い乾燥機": "kitchen_dishwasher",
    "キッチン（下） コンセント": "kitchen_lower_outlets",
    "キッチン（上） コンセント": "kitchen_upper_outlets",
    "シャワー洗面納戸 照明＆コンセント": "shower_lighting_and_outlets",
    "ダイニング エアコン": "dining_air_conditioner",
    "ダイニング 照明＆コンセント": "dining_lighting_and_outlets",
    "ダイニング（南） 照明＆コンセント": "dining_south_lighting_and_outlets",
    "ダイニング（北） コンセント": "dining_north_outlets",
    "リビング エアコン": "living_air_conditioner",
    "リビング 非常警報設備": "living_alarm_system",
    "リビング（南） 照明＆コンセント": "living_south_lighting_and_outlets",
    "リビング（北） 照明＆コンセント": "living_north_lighting_and_outlets",
    "階段・２階共用 照明＆コンセント": "stairs_2_common_lighting_and_outlets",
    "玄関・１階廊下 照明＆コンセント": "foyer_lighting_and_outlets",
    "書斎 エアコン": "den_air_conditioner",
    "書斎 照明＆コンセント": "den_lighting_and_outlets",
    "寝室 エアコン": "bedroom_air_conditioner",
    "寝室・クロゼット 照明＆コンセント": "bedroom_closet_lighting_and_outlets",
    "寝室（東） 照明＆コンセント": "bedroom_east_lighting_and_outlets",
    "水消費量": "water_consumption",
    "洗面 照明＆コンセント": "washroom_lighting_and_outlets",
    "洗面 洗濯機": "washroom_washing_machine",
    "洗面 暖房器": "washroom_heater",
    "洋室１父母部屋 エアコン": "room1_air_conditioner",
    "洋室１父母部屋 照明＆コンセント": "room1_lighting_and_outlets",
    "洋室２ エアコン": "room2_air_conditioner",
    "洋室２ 照明＆コンセント": "room2_lighting_and_outlets",
    "洋室３子供部屋 エアコン": "room3_air_conditioner",
    "洋室３子供部屋 照明＆コンセント": "room3_lighting_and_outlets",
    "浴室 浴室乾燥機": "bathroom_dryer",
}


# 日本語名をエンティティ名に変換
def ja_to_entity(name: str) -> str:
    """Translate Japanese name to entity name."""
    return ja_to_entity_translation_dict.get(name, name)
