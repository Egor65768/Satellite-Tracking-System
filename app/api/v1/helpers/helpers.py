from fastapi import HTTPException


async def raise_if_object_none(object_to_be_checked, status_code: int, detail: str):
    if not object_to_be_checked:
        raise HTTPException(status_code=status_code, detail=detail)
