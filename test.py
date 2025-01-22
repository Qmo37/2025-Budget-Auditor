import json
import pandas as pd

class ProposalSearcher:
    def __init__(self, json_file, csv_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            self.categories_data = json.load(f)
        self.proposals_df = pd.read_csv(csv_file, encoding='utf-8')
        self.category_mapping = self._create_category_mapping()

    def _create_category_mapping(self):
        mapping = {}
        for cat_dict in self.categories_data['categories']:
            for key, values in cat_dict.items():
                for value in values:
                    mapping[value] = key
        return mapping

    def get_unique_values(self):
        return {
            'categories': sorted(list(set(self.proposals_df['category'].dropna()))),
            'proposers': sorted(list(set(self.proposals_df['who'].dropna()))),
            'results': sorted(list(set(self.proposals_df['result'].dropna()))),
            'full_names': sorted(list(set(self.proposals_df['full_name'].dropna())))
        }

    def search_proposals(self, category=None, proposer=None, result=None, full_name=None):
        filtered_df = self.proposals_df.copy()

        if category:
            filtered_df = filtered_df[filtered_df['category'] == category]
        if proposer:
            filtered_df = filtered_df[filtered_df['who'].str.contains(proposer, na=False)]
        if result:
            filtered_df = filtered_df[filtered_df['result'] == result]
        if full_name:
            filtered_df = filtered_df[filtered_df['full_name'] == full_name]

        return filtered_df

    def search_by_keyword(self, keyword, search_fields=None):
        """
        Search proposals by keyword with more options

        Parameters:
        - keyword: str, the search term
        - search_fields: list of str, fields to search in (default: ['content'])
        """
        if not keyword:
            return pd.DataFrame()

        if search_fields is None:
            search_fields = ['content']

        # Create mask for each field
        masks = []
        for field in search_fields:
            if field in self.proposals_df.columns:
                mask = self.proposals_df[field].str.contains(keyword, case=False, na=False)
                masks.append(mask)

        # Combine masks with OR operation
        final_mask = pd.concat(masks, axis=1).any(axis=1)
        return self.proposals_df[final_mask]

class SearchMenu:
    def __init__(self, searcher):
        self.searcher = searcher
        self.unique_values = searcher.get_unique_values()

    def get_category_input(self):
        print("\n可用類別:")
        for i, cat in enumerate(self.unique_values['categories'], 1):
            print(f"{i}. {cat}")
        cat_choice = input("請選擇類別編號 (直接按Enter跳過): ")
        if cat_choice.isdigit() and 1 <= int(cat_choice) <= len(self.unique_values['categories']):
            return self.unique_values['categories'][int(cat_choice)-1]
        return None

    def get_proposer_input(self):
        proposer = input("\n請輸入提案人姓名 (直接按Enter跳過): ")
        return proposer if proposer else None

    def get_result_input(self):
        print("\n可用結果:")
        for i, result in enumerate(self.unique_values['results'], 1):
            print(f"{i}. {result}")
        result_choice = input("請選擇結果編號 (直接按Enter跳過): ")
        if result_choice.isdigit() and 1 <= int(result_choice) <= len(self.unique_values['results']):
            return self.unique_values['results'][int(result_choice)-1]
        return None

    def get_department_input(self):
        print("\n可用部門:")
        for i, name in enumerate(self.unique_values['full_names'], 1):
            print(f"{i}. {name}")
        name_choice = input("請選擇部門編號 (直接按Enter跳過): ")
        if name_choice.isdigit() and 1 <= int(name_choice) <= len(self.unique_values['full_names']):
            return self.unique_values['full_names'][int(name_choice)-1]
        return None

    def get_keyword_input(self):
        """Get keyword input with advanced options"""
        print("\n=== 關鍵字搜尋 ===")
        print("搜尋選項:")
        print("1. 只搜尋內容")
        print("2. 搜尋所有欄位")

        search_option = input("請選擇搜尋選項 (1-2): ")
        keyword = input("請輸入搜尋關鍵字: ")

        if not keyword:
            return None, None

        search_fields = ['content']
        if search_option == '2':
            search_fields = ['content', 'who', 'full_name', 'category', 'result']

        return keyword, search_fields

    def display_full_content_results(self, results):
        """Display full content of search results"""
        if len(results) > 0:
            print(f"\n找到 {len(results)} 筆結果:")
            for idx, row in results.iterrows():
                print("\n" + "="*50)
                print(f"提案 {idx+1}")
                print("="*50)
                print(f"類別: {row['category']}")
                print(f"部門: {row['full_name']}")
                print(f"提案人: {row['who']}")
                print(f"結果: {row['result']}")
                print(f"時間地點: {row['time_place']}")
                if pd.notna(row['cost']):
                    print(f"金額: {row['cost']}")
                print("\n完整內容:")
                print(row['content'])
        else:
            print("\n未找到符合關鍵字的提案")

    def display_menu(self):
        print("\n=== 提案搜尋系統 ===")
        print("1. 依類別搜尋")
        print("2. 依提案人搜尋")
        print("3. 依結果搜尋")
        print("4. 依部門名稱搜尋")
        print("5. 多重條件搜尋")
        print("6. 關鍵字搜尋")
        print("7. 退出")

def main():
    searcher = ProposalSearcher('bucket_2025.json', 'budget.csv')
    menu = SearchMenu(searcher)

    while True:
            menu.display_menu()
            choice = input("請選擇搜尋方式 (1-7): ")

            if choice == '7':
                break

            if choice == '6':
                # Enhanced keyword search
                keyword, search_fields = menu.get_keyword_input()
                if keyword:
                    results = searcher.search_by_keyword(keyword, search_fields)
                    menu.display_full_content_results(results)
                continue

            search_params = {}

            if choice in ['1', '5']:
                category = menu.get_category_input()
                if category:
                    search_params['category'] = category

            if choice in ['2', '5']:
                proposer = menu.get_proposer_input()
                if proposer:
                    search_params['proposer'] = proposer

            if choice in ['3', '5']:
                result = menu.get_result_input()
                if result:
                    search_params['result'] = result

            if choice in ['4', '5']:
                department = menu.get_department_input()
                if department:
                    search_params['full_name'] = department

            results = searcher.search_proposals(**search_params)
            menu.display_full_content_results(results)

if __name__ == "__main__":
    main()
