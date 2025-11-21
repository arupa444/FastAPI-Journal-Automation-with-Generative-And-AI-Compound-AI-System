from Apps.library_import import APIRouter, JSONResponse, HTTPException, Path
from Apps.models_journal import PulsusInputStr, UpdateInputPartJournal
from Apps.services.io_service import IOService

router = APIRouter(prefix="/journal", tags=["Journal Management"])


@router.get("/all")
def view_all():
    data = IOService.fetchInputData()
    return data or {"message": "No journal data found."}


@router.get("/{journal_id}")
def get_journal(
    journal_id: str = Path(
        ..., description="Enter journal ID", examples="J001", max_length=4
    )
):
    data = IOService.fetchInputData()
    if journal_id in data:
        return data[journal_id]
    raise HTTPException(status_code=404, detail="Journal not found")


@router.post("/add")
def create_journal(journal: PulsusInputStr):
    data = IOService.fetchInputData()
    if journal.id in data:
        raise HTTPException(status_code=400, detail="Journal ID already exists.")
    data[journal.id] = journal.model_dump(exclude=["id"])
    IOService.saveInputData(data)
    return JSONResponse(
        status_code=200, content={"message": "Journal added successfully"}
    )


@router.put("/update/{journal_id}")
def updateInpJournal(journal_id: str, update_data: UpdateInputPartJournal):
    data = IOService.fetchInputData()

    if journal_id not in data:
        raise HTTPException(status_code=404, detail="Journal Input not found")

    tempStoreInfo = data[journal_id]
    tempStoreInfo["id"] = journal_id

    updatedInfo = update_data.model_dump(exclude_unset=True)

    for key, value in updatedInfo.items():
        tempStoreInfo[key] = value

    validateInpJournal = UpdateInputPartJournal(**tempStoreInfo)

    data[journal_id] = validateInpJournal.model_dump(exclude=["id"])
    IOService.saveInputData(data)

    return JSONResponse(status_code=200, content={"message": "Successfully updated"})


@router.delete("/delete/{journal_id}")
def delete_journal(journal_id: str):
    print("DELETE route reached with:", journal_id)
    data = IOService.fetchInputData()
    if journal_id not in data:
        raise HTTPException(status_code=404, detail="Journal not found")
    del data[journal_id]
    IOService.saveInputData(data)
    print("Keys after delete:", data.keys())
    return JSONResponse(
        status_code=200, content={"message": f"Perfectly deleted the {journal_id}"}
    )
