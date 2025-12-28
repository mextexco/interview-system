"""
Data Validator / データバリデーター
データの矛盾検出と地理的検証を行うモジュール

Detects contradictions in extracted data and validates geographic information.
"""

from typing import Dict, List, Tuple, Optional, Any
import re


class DataValidator:
    """
    Data validation and contradiction detection
    データバリデーションと矛盾検出
    """

    # 矛盾検出ルール / Contradiction detection rules
    CONTRADICTION_RULES = {
        "基本プロフィール": {
            "家族構成": {
                "single_indicators": [
                    "1人暮らし", "独身", "一人暮らし", "単身",
                    "ひとり暮らし", "独り暮らし", "一人", "単独"
                ],
                "family_indicators": [
                    "家族", "両親", "妻", "夫", "子供", "子", "父", "母",
                    "兄", "弟", "姉", "妹", "祖父", "祖母", "孫",
                    "人家族", "世帯", "同居"
                ],
                "check_type": "mutual_exclusive"
            },
            "住居状況": {
                "rental_indicators": [
                    "賃貸", "マンション", "アパート", "借家",
                    "賃貸マンション", "賃貸アパート", "借りている"
                ],
                "owned_indicators": [
                    "持ち家", "一戸建て", "自宅", "マイホーム",
                    "購入", "所有", "建てた", "買った"
                ],
                "check_type": "mutual_exclusive"
            }
        },
        "現在の生活": {
            "勤務状況": {
                "employed_indicators": [
                    "会社員", "正社員", "勤務", "働いている", "就業",
                    "サラリーマン", "OL", "会社勤め", "フルタイム"
                ],
                "unemployed_indicators": [
                    "無職", "失業", "休職", "退職", "仕事していない",
                    "働いていない", "ニート", "求職中"
                ],
                "check_type": "mutual_exclusive"
            }
        }
    }

    # 都道府県と市区町村のマッピング（主要都市のみ）
    # Prefecture-City mappings (major cities only)
    GEOGRAPHY_MAP = {
        "北海道": ["札幌市", "函館市", "小樽市", "旭川市", "室蘭市", "釧路市", "帯広市", "北見市"],
        "青森県": ["青森市", "弘前市", "八戸市"],
        "岩手県": ["盛岡市", "宮古市", "一関市"],
        "宮城県": ["仙台市", "石巻市", "大崎市"],
        "秋田県": ["秋田市", "横手市", "大館市"],
        "山形県": ["山形市", "米沢市", "鶴岡市"],
        "福島県": ["福島市", "会津若松市", "郡山市", "いわき市"],
        "茨城県": ["水戸市", "つくば市", "日立市", "土浦市"],
        "栃木県": ["宇都宮市", "小山市", "栃木市"],
        "群馬県": ["前橋市", "高崎市", "太田市"],
        "埼玉県": ["さいたま市", "川越市", "川口市", "所沢市", "越谷市", "草加市", "春日部市", "熊谷市"],
        "千葉県": ["千葉市", "市川市", "船橋市", "松戸市", "柏市", "市原市"],
        "東京都": [
            "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区",
            "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区", "豊島区",
            "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区",
            "八王子市", "立川市", "武蔵野市", "三鷹市", "府中市", "調布市", "町田市"
        ],
        "神奈川県": ["横浜市", "川崎市", "相模原市", "横須賀市", "平塚市", "鎌倉市", "藤沢市", "小田原市"],
        "新潟県": ["新潟市", "長岡市", "上越市"],
        "富山県": ["富山市", "高岡市"],
        "石川県": ["金沢市", "小松市"],
        "福井県": ["福井市", "敦賀市"],
        "山梨県": ["甲府市", "富士吉田市"],
        "長野県": ["長野市", "松本市", "上田市", "飯田市"],
        "岐阜県": ["岐阜市", "大垣市", "高山市"],
        "静岡県": ["静岡市", "浜松市", "沼津市", "富士市"],
        "愛知県": ["名古屋市", "豊橋市", "岡崎市", "一宮市", "豊田市"],
        "三重県": ["津市", "四日市市", "伊勢市"],
        "滋賀県": ["大津市", "彦根市", "長浜市"],
        "京都府": ["京都市", "宇治市", "亀岡市"],
        "大阪府": ["大阪市", "堺市", "豊中市", "吹田市", "高槻市", "枚方市", "茨木市", "八尾市", "東大阪市"],
        "兵庫県": ["神戸市", "姫路市", "尼崎市", "明石市", "西宮市", "芦屋市", "伊丹市", "宝塚市"],
        "奈良県": ["奈良市", "橿原市", "生駒市"],
        "和歌山県": ["和歌山市", "田辺市"],
        "鳥取県": ["鳥取市", "米子市"],
        "島根県": ["松江市", "出雲市"],
        "岡山県": ["岡山市", "倉敷市", "津山市"],
        "広島県": ["広島市", "福山市", "呉市", "東広島市"],
        "山口県": ["下関市", "宇部市", "山口市"],
        "徳島県": ["徳島市", "阿南市"],
        "香川県": ["高松市", "丸亀市"],
        "愛媛県": ["松山市", "今治市", "新居浜市"],
        "高知県": ["高知市", "南国市"],
        "福岡県": ["福岡市", "北九州市", "久留米市", "飯塚市", "大牟田市"],
        "佐賀県": ["佐賀市", "唐津市"],
        "長崎県": ["長崎市", "佐世保市", "諫早市"],
        "熊本県": ["熊本市", "八代市", "天草市"],
        "大分県": ["大分市", "別府市", "中津市"],
        "宮崎県": ["宮崎市", "都城市", "延岡市"],
        "鹿児島県": ["鹿児島市", "霧島市", "鹿屋市"],
        "沖縄県": ["那覇市", "沖縄市", "浦添市", "名護市"]
    }

    def __init__(self):
        """Initialize the validator"""
        pass

    def check_contradiction(
        self,
        category: str,
        new_key: str,
        new_value: str,
        existing_data: List[Dict]
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if new data contradicts existing data
        新しいデータが既存データと矛盾しないかチェック

        Args:
            category: データカテゴリ / Data category
            new_key: 新しいデータのキー / New data key
            new_value: 新しいデータの値 / New data value
            existing_data: 既存データのリスト / List of existing data

        Returns:
            (is_valid, conflict_message):
                - is_valid: True if no contradiction, False if contradiction found
                - conflict_message: Description of the contradiction (if any)
        """
        # カテゴリが矛盾ルールに存在しない場合はスキップ
        if category not in self.CONTRADICTION_RULES:
            return True, None

        category_rules = self.CONTRADICTION_RULES[category]

        # キーが矛盾ルールに存在しない場合はスキップ
        if new_key not in category_rules:
            return True, None

        rule = category_rules[new_key]
        check_type = rule.get("check_type")

        if check_type == "mutual_exclusive":
            # 相互排他的なルールのチェック
            return self._check_mutual_exclusive(
                new_key, new_value, existing_data, rule
            )

        return True, None

    def _check_mutual_exclusive(
        self,
        new_key: str,
        new_value: str,
        existing_data: List[Dict],
        rule: Dict
    ) -> Tuple[bool, Optional[str]]:
        """
        Check mutual exclusive rules
        相互排他的なルールをチェック

        Example: "1人暮らし" and "5人家族" cannot coexist
        """
        new_value_lower = new_value.lower()

        # 新しい値がどのグループに属するか判定
        new_value_group = None
        for group_name in rule.keys():
            if group_name == "check_type":
                continue
            indicators = rule[group_name]
            for indicator in indicators:
                if indicator in new_value_lower:
                    new_value_group = group_name
                    break
            if new_value_group:
                break

        # グループに属さない場合はチェックしない
        if not new_value_group:
            return True, None

        # 既存データをチェック
        for existing_item in existing_data:
            if existing_item.get("key") != new_key:
                continue

            existing_value = str(existing_item.get("value", "")).lower()

            # 既存データがどのグループに属するか判定
            for group_name in rule.keys():
                if group_name == "check_type" or group_name == new_value_group:
                    continue

                indicators = rule[group_name]
                for indicator in indicators:
                    if indicator in existing_value:
                        # 矛盾を発見
                        conflict_msg = (
                            f"Contradiction in {new_key}: "
                            f"New value '{new_value}' ({new_value_group}) "
                            f"contradicts existing '{existing_item['value']}' ({group_name})"
                        )
                        return False, conflict_msg

        return True, None

    def validate_geographic_data(self, value: str) -> Dict[str, Any]:
        """
        Validate geographic data (prefecture + city combination)
        地理データを検証（都道府県と市区町村の組み合わせ）

        Args:
            value: 住所文字列 / Address string

        Returns:
            Dictionary with validation result:
            {
                "valid": bool,
                "prefecture": str (if found),
                "city": str (if found),
                "error": str (if invalid),
                "warning": str (if unverified)
            }
        """
        result = {
            "valid": True,
            "original": value
        }

        # 都道府県を検出
        detected_prefecture = None
        for prefecture in self.GEOGRAPHY_MAP.keys():
            if prefecture in value:
                detected_prefecture = prefecture
                break

        if not detected_prefecture:
            # 都道府県が見つからない場合は検証をスキップ
            result["warning"] = "Prefecture not detected, skipping validation"
            return result

        result["prefecture"] = detected_prefecture

        # 市区町村を検出
        detected_city = None
        possible_cities = self.GEOGRAPHY_MAP[detected_prefecture]

        for city in possible_cities:
            # 完全一致または部分一致（市を除いた名前）
            city_base = city.replace("市", "").replace("区", "").replace("町", "").replace("村", "")
            if city in value or (len(city_base) >= 2 and city_base in value):
                detected_city = city
                break

        # 検出された都道府県のリストにない場合、他の都道府県の市区町村かチェック
        if not detected_city:
            # 他の都道府県の市区町村かチェック
            for other_prefecture, cities in self.GEOGRAPHY_MAP.items():
                if other_prefecture == detected_prefecture:
                    continue
                for city in cities:
                    # 完全一致または部分一致（市を除いた名前）
                    city_base = city.replace("市", "").replace("区", "").replace("町", "").replace("村", "")
                    if city in value or (len(city_base) >= 2 and city_base in value):
                        # 矛盾を発見（例: 東京都横浜）
                        result["valid"] = False
                        result["error"] = (
                            f"Geographic contradiction: {city} belongs to "
                            f"{other_prefecture}, not {detected_prefecture}"
                        )
                        result["correct_prefecture"] = other_prefecture
                        result["detected_city"] = city
                        return result

            # 市区町村がリストにない（未検証）
            city_part = value.replace(detected_prefecture, "").strip()
            if city_part:
                result["city"] = city_part
                result["warning"] = (
                    f"City '{city_part}' not in verified list for {detected_prefecture}"
                )
        else:
            # 市区町村が正しく検出された
            result["city"] = detected_city
            result["valid"] = True

        return result

    def validate_data_point(
        self,
        category: str,
        key: str,
        value: Any,
        existing_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Complete validation for a single data point
        単一のデータポイントを完全に検証

        Returns:
            {
                "valid": bool,
                "contradictions": List[str],
                "warnings": List[str],
                "geographic_validation": Dict (if applicable)
            }
        """
        validation_result = {
            "valid": True,
            "contradictions": [],
            "warnings": []
        }

        # 矛盾チェック
        is_valid, conflict_msg = self.check_contradiction(
            category, key, value, existing_data
        )
        if not is_valid:
            validation_result["valid"] = False
            validation_result["contradictions"].append(conflict_msg)

        # 地理的検証（住所関連のキーの場合）
        if key in ["住所", "居住地", "出身地", "勤務地"]:
            geo_result = self.validate_geographic_data(str(value))
            validation_result["geographic_validation"] = geo_result

            if not geo_result.get("valid"):
                validation_result["valid"] = False
                validation_result["contradictions"].append(
                    geo_result.get("error", "Geographic validation failed")
                )
            elif "warning" in geo_result:
                validation_result["warnings"].append(geo_result["warning"])

        return validation_result

    def normalize_value(self, category: str, key: str, value: Any) -> Any:
        """
        Normalize value based on category and key
        カテゴリーとキーに基づいて値を正規化

        Args:
            category: カテゴリー名
            key: キー名
            value: 正規化する値

        Returns:
            正規化された値（構造化データまたは元の値）
        """
        # 年収・収入の正規化
        if key in ["年収", "収入", "給料", "所得"]:
            return self._normalize_income(value)

        # 年齢の正規化
        if key in ["年齢", "歳", "年代", "年齢層"]:
            return self._normalize_age(value)

        # 住所の正規化（地理的検証を含む）
        if key in ["住所", "居住地", "出身地", "勤務地"]:
            return self._normalize_address(value)

        # その他の値はそのまま返す
        return value

    def _normalize_income(self, value: str) -> Dict[str, Any]:
        """
        Normalize income values
        年収・収入の値を正規化

        Examples:
            "300万" → {"amount": 3000000, "currency": "JPY", "original": "300万"}
            "300万円" → {"amount": 3000000, "currency": "JPY", "original": "300万円"}
            "500万くらい" → {"amount": 5000000, "currency": "JPY", "original": "500万くらい", "approximate": true}
        """
        import re

        value_str = str(value)
        result = {
            "original": value_str,
            "currency": "JPY"
        }

        # 数値抽出パターン
        # "300万", "300万円", "3000000", "300", etc.
        pattern = r'(\d+(?:\.\d+)?)\s*(万|億|千)?'
        match = re.search(pattern, value_str)

        if match:
            number = float(match.group(1))
            unit = match.group(2)

            # 単位に応じて金額を計算
            if unit == "億":
                amount = int(number * 100000000)
            elif unit == "万":
                amount = int(number * 10000)
            elif unit == "千":
                amount = int(number * 1000)
            else:
                amount = int(number)

            result["amount"] = amount

            # 概算かどうかを判定
            if any(word in value_str for word in ["くらい", "ぐらい", "程度", "前後", "約"]):
                result["approximate"] = True

            return result

        # パースできない場合は元の値を返す
        return value_str

    def _normalize_age(self, value: str) -> Dict[str, Any]:
        """
        Normalize age values
        年齢の値を正規化

        Examples:
            "30歳" → {"age": 30, "original": "30歳"}
            "50代" → {"age_range": [50, 59], "original": "50代"}
            "30代前半" → {"age_range": [30, 34], "original": "30代前半"}
            "30代後半" → {"age_range": [35, 39], "original": "30代後半"}
        """
        import re

        value_str = str(value)
        result = {
            "original": value_str
        }

        # "30歳" パターン
        age_match = re.search(r'(\d+)\s*歳', value_str)
        if age_match:
            result["age"] = int(age_match.group(1))
            return result

        # "30代" パターン
        decade_match = re.search(r'(\d+)\s*代', value_str)
        if decade_match:
            decade = int(decade_match.group(1))

            # 前半・後半の判定
            if "前半" in value_str:
                result["age_range"] = [decade, decade + 4]
            elif "後半" in value_str:
                result["age_range"] = [decade + 5, decade + 9]
            else:
                result["age_range"] = [decade, decade + 9]

            return result

        # "20-30" パターン
        range_match = re.search(r'(\d+)\s*[-~〜]\s*(\d+)', value_str)
        if range_match:
            result["age_range"] = [int(range_match.group(1)), int(range_match.group(2))]
            return result

        # パースできない場合は元の値を返す
        return value_str

    def _normalize_address(self, value: str) -> Dict[str, Any]:
        """
        Normalize address with geographic validation
        住所を地理的検証とともに正規化

        Examples:
            "東京都渋谷区" → {
                "prefecture": "東京都",
                "city": "渋谷区",
                "original": "東京都渋谷区",
                "validated": True
            }
            "東京都横浜" → エラー（横浜は神奈川県）
        """
        geo_result = self.validate_geographic_data(str(value))

        # 検証結果を構造化データとして返す
        result = {
            "original": value,
            "validated": geo_result.get("valid", False)
        }

        if "prefecture" in geo_result:
            result["prefecture"] = geo_result["prefecture"]
        if "city" in geo_result:
            result["city"] = geo_result["city"]
        if "error" in geo_result:
            result["error"] = geo_result["error"]
        if "warning" in geo_result:
            result["warning"] = geo_result["warning"]

        return result


# 使用例 / Usage example
if __name__ == "__main__":
    # テスト / Test
    validator = DataValidator()

    # Test 1: 家族構成の矛盾チェック
    existing = [
        {"key": "家族構成", "value": "1人暮らし"}
    ]
    is_valid, msg = validator.check_contradiction(
        "基本プロフィール",
        "家族構成",
        "5人家族",
        existing
    )
    print(f"Test 1 - Contradiction check: Valid={is_valid}, Message={msg}")

    # Test 2: 地理的検証（矛盾あり）
    geo_result = validator.validate_geographic_data("東京都横浜")
    print(f"Test 2 - Geographic validation: {geo_result}")

    # Test 3: 地理的検証（正常）
    geo_result = validator.validate_geographic_data("東京都渋谷区")
    print(f"Test 3 - Geographic validation: {geo_result}")

    # Test 4: 完全な検証
    validation = validator.validate_data_point(
        "基本プロフィール",
        "住所",
        "東京都横浜",
        []
    )
    print(f"Test 4 - Complete validation: {validation}")
