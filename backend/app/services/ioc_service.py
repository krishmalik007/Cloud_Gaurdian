from fastapi import HTTPException, status

from app.storage.ioc_repository import ioc_repository


class IOCService:

    # -----------------------------------
    # Create IOC
    # -----------------------------------
    def create_ioc(self, ioc: dict):

        existing = ioc_repository.search_value(
            ioc["value"]
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="IOC already exists."
            )

        return ioc_repository.create_ioc(ioc)

    # -----------------------------------
    # Get IOC
    # -----------------------------------
    def get_ioc(self, ioc_id: str):

        ioc = ioc_repository.get_ioc(ioc_id)

        if not ioc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IOC not found."
            )

        return ioc

    # -----------------------------------
    # Get All IOCs
    # -----------------------------------
    def get_all_iocs(self):

        return ioc_repository.get_all_iocs()

    # -----------------------------------
    # Update IOC
    # -----------------------------------
    def update_ioc(
        self,
        ioc_id: str,
        updates: dict
    ):

        ioc = ioc_repository.get_ioc(ioc_id)

        if not ioc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IOC not found."
            )

        return ioc_repository.update_ioc(
            ioc_id,
            updates
        )

    # -----------------------------------
    # Delete IOC
    # -----------------------------------
    def delete_ioc(self, ioc_id: str):

        deleted = ioc_repository.delete_ioc(
            ioc_id
        )

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="IOC not found."
            )

        return {
            "message": "IOC deleted successfully."
        }

    # -----------------------------------
    # Search IOC by Value
    # -----------------------------------
    def search_value(self, value: str):

        return ioc_repository.search_value(value)


ioc_service = IOCService()