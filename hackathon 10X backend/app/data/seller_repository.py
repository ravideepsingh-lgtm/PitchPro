from app.data.excel_loader import excel_loader

class SellerRepository:
    def get_glids(self, limit: int = 100, offset: int = 0, specific_glids: list = None) -> list:
        """
        Retrieves a list of GLIDs from the master client_base sheet.
        """
        if specific_glids:
            return specific_glids
            
        cb_df = excel_loader.get_df("Client Base")
        if cb_df.empty or 'glusr_usr_id' not in cb_df.columns:
            return []
            
        # Get unique glids, dropping nulls
        all_glids = cb_df['glusr_usr_id'].dropna().unique().tolist()
        
        # Convert to int to be safe
        all_glids = [int(g) for g in all_glids if str(g).replace('.0','').isdigit()]
        
        # Apply offset and limit
        end_idx = offset + limit
        return all_glids[offset:end_idx]

    def get_total_count(self) -> int:
        cb_df = excel_loader.get_df("Client Base")
        if cb_df.empty or 'glusr_usr_id' not in cb_df.columns:
            return 0
        return cb_df['glusr_usr_id'].nunique()

seller_repository = SellerRepository()
