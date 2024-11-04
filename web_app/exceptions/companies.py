from web_app.exceptions.base import ObjectNotFoundException


class CompanyNotFoundException(ObjectNotFoundException):
    def __init__(self, company_id: int):
        super().__init__(object_type="Company", field=f"ID {company_id}")


class OwnerNotFoundException(ObjectNotFoundException):
    def __init__(self, company_id: int):
        super().__init__(object_type="Owner", field=f"company's ID {company_id}")
