"""Japanese to English translation for ecomane integration."""

import re
import unicodedata

# 変換表の定義
translation_dict = {
    "太陽光": "Solar_Power",
    "キッチン": "Kitchen",
    "照明＆コンセント": "Lighting_and_Outlets",
    "コンセント": "Outlets",
    "ダイニング": "Dining",
    "北": "North",
    "南": "South",
    "リビング": "Living_Room",
    "洋室": "Western_style_Room",
    "父母部屋": "Parents_Room",
    "洗面": "Washroom",
    "玄関": "Entrance",
    "階廊下": "Floor_Hallway",
    "寝室": "Bedroom",
    "東": "East",
    "クロゼット": "Closet",
    "書斎": "Study",
    "シャワー": "Shower",
    "納戸": "Storage",
    "階段": "Stairs",
    "共用": "Common",
    "上": "Upper",
    "下": "Lower",
    "食器洗い乾燥機": "Dishwasher",
    "洗濯機": "Washing_Machine",
    "浴室": "Bathroom",
    "浴室乾燥機": "Bathroom_Dryer",
    "暖房器": "Heater",
    "トイレ": "Toilet",
    "子供部屋": "Childrens_Room",
    "エアコン": "Air_Conditioner",
    "非常警報設備": "Emergency_Alarm_System",
    "イシューなし": "No_issues",
    "このエンティティには、使用できる状態がありません。": "This_entity_has_no_available_states",
    "購入電気量": "Electricity_purchased",
    "太陽光発電量": "Solar_Power_Energy",
    "ガス消費量": "Gas_Consumption",
    "水消費量": "Water_Consumption",
    "CO2排出量": "CO2_Emissions",
    "CO2削減量": "CO2_Reduction",
    "売電量": "Electricity_sales",
}

# def extract_and_translate(text):
#     # 日本語および記号の連続を抽出
#     # japanese_words = re.findall(r"[ぁ-んァ-ン一-龥、。！？（）・＆]+", text)
#     # 日本語（漢字、ひらがな、カタカナ）および関連する記号の連続を抽出
#     # japanese_words = re.findall(r"[一-龥ぁ-んァ-ン、。！？（）・＆]+", text)
#     # # 日本語（漢字、ひらがな、カタカナ、長音記号）および関連する記号の連続を抽出
#     japanese_words = re.findall(r"[一-龥ぁ-んァ-ンー、。！？（）・＆]+", text)
#     print(japanese_words)
#     translated_words = []

#     for word in japanese_words:
#         # 変換表に基づいて翻訳
#         translated = translation_dict.get(word, word)
#         # 空白をアンダースコアに変換
#         translated = translated.replace(" ", "_")
#         # Python変数名として使用できない文字をアンダースコアに変換
#         translated = re.sub(r"[^\w]", "_", translated)
#         translated_words.append(translated)

#     print(translated_words)
#     return translated_words


# テスト用の入力テキスト
input_text = """
太陽光
１階トイレ コンセント
CO2削減量
CO2削減量
CO2排出量
CO2排出量
ガス消費量
ガス消費量
キッチン 照明＆コンセント
キッチン 食器洗い乾燥機
キッチン（下） コンセント
キッチン（上） コンセント
シャワー洗面納戸 照明＆コンセント
ダイニング エアコン
ダイニング 照明＆コンセント
ダイニング（南） 照明＆コンセント
ダイニング（北） コンセント
リビング エアコン
リビング 非常警報設備
リビング（南） 照明＆コンセント
リビング（北） 照明＆コンセント
階段・２階共用 照明＆コンセント
玄関・１階廊下 照明＆コンセント
購入電気量
購入電気量
書斎 エアコン
書斎 照明＆コンセント
寝室 エアコン
寝室・クロゼット 照明＆コンセント
寝室（東） 照明＆コンセント
水消費量
水消費量
洗面 照明＆コンセント
洗面 洗濯機
洗面 暖房器
太陽光発電量
太陽光発電量
売電量
売電量
洋室１父母部屋 エアコン
洋室１父母部屋 照明＆コンセント
洋室２ エアコン
洋室２ 照明＆コンセント
洋室３子供部屋 エアコン
洋室３子供部屋 照明＆コンセント
浴室 浴室乾燥機
"""


def translate_japanese_to_english(text):
    """Translate Japanese text to English."""

    # 辞書内のすべての項目に対して変換を適用
    for jp, en in sorted(
        translation_dict.items(), key=lambda x: len(x[0]), reverse=True
    ):
        text = text.replace(jp, en)

    # print(f"{text=}")
    # 残りの日本語文字、記号、スペースをアンダースコアに変換
    text = re.sub(r"[一-龥ぁ-んァ-ンー、。！？（）・＆ 　]+", "_", text)
    # 全角英数字を半角に変換
    text = unicodedata.normalize("NFKC", text)
    # print(f"{text=}")
    # 連続するアンダースコアを1つに置換し、先頭と末尾のアンダースコアを削除
    text = re.sub(r"_{2,}", "_", text).strip("_")

    # 英字の大文字を小文字に変換
    return text.lower()


# # # テキストを処理して出力
# print(f"{input_text=}")
# result = translate_japanese_to_english(input_text, translation_dict)
# print(result)
