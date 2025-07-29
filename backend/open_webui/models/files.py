import logging
import time
from typing import Optional

from open_webui.internal.db import Base, JSONField, get_db
from open_webui.env import SRC_LOG_LEVELS
from pydantic import BaseModel, ConfigDict
from sqlalchemy import BigInteger, Column, String, Text, JSON

log = logging.getLogger(__name__)
log.setLevel(SRC_LOG_LEVELS["MODELS"])

####################
# Files DB Schema
####################


class File(Base):
    __tablename__ = "file"
    id = Column(String, primary_key=True)
    user_id = Column(String)
    hash = Column(Text, nullable=True)

    filename = Column(Text)
    path = Column(Text, nullable=True)

    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    access_control = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class FileModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    hash: Optional[str] = None

    filename: str
    path: Optional[str] = None

    data: Optional[dict] = None
    meta: Optional[dict] = None

    access_control: Optional[dict] = None

    created_at: Optional[int]  # timestamp in epoch
    updated_at: Optional[int]  # timestamp in epoch


####################
# Forms
####################


class FileMeta(BaseModel):
    name: Optional[str] = None
    content_type: Optional[str] = None
    size: Optional[int] = None

    model_config = ConfigDict(extra="allow")


class FileModelResponse(BaseModel):
    id: str
    user_id: str
    hash: Optional[str] = None

    filename: str
    data: Optional[dict] = None
    meta: FileMeta

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch

    model_config = ConfigDict(extra="allow")


class FileMetadataResponse(BaseModel):
    id: str
    meta: dict
    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


class FileForm(BaseModel):
    id: str
    hash: Optional[str] = None
    filename: str
    path: str
    data: dict = {}
    meta: dict = {}
    access_control: Optional[dict] = None


class FilesTable:
    def insert_new_file(self, user_id: str, form_data: FileForm) -> Optional[FileModel]:
        log.info(f"Inserting new file for user {user_id}, file_id: {form_data.id}, filename: {form_data.filename}")
        with get_db() as db:
            file = FileModel(
                **{
                    **form_data.model_dump(),
                    "user_id": user_id,
                    "created_at": int(time.time()),
                    "updated_at": int(time.time()),
                }
            )

            try:
                result = File(**file.model_dump())
                db.add(result)
                db.commit()
                db.refresh(result)
                if result:
                    log.info(f"Successfully inserted file {result.id} for user {user_id}")
                    return FileModel.model_validate(result)
                else:
                    log.warning(f"Failed to insert file {form_data.id} for user {user_id} - no result returned")
                    return None
            except Exception as e:
                log.exception(f"Error inserting a new file {form_data.id} for user {user_id}: {e}")
                return None

    def get_file_by_id(self, id: str) -> Optional[FileModel]:
        log.debug(f"Retrieving file by id: {id}")
        with get_db() as db:
            try:
                file = db.get(File, id)
                if file:
                    log.debug(f"Successfully retrieved file {id}")
                    return FileModel.model_validate(file)
                else:
                    log.warning(f"File not found with id: {id}")
                    return None
            except Exception as e:
                log.exception(f"Error retrieving file {id}: {e}")
                return None

    def get_file_metadata_by_id(self, id: str) -> Optional[FileMetadataResponse]:
        log.debug(f"Retrieving file metadata by id: {id}")
        with get_db() as db:
            try:
                file = db.get(File, id)
                if file:
                    log.debug(f"Successfully retrieved file metadata for {id}")
                    return FileMetadataResponse(
                        id=file.id,
                        meta=file.meta,
                        created_at=file.created_at,
                        updated_at=file.updated_at,
                    )
                else:
                    log.warning(f"File not found for metadata retrieval: {id}")
                    return None
            except Exception as e:
                log.exception(f"Error retrieving file metadata {id}: {e}")
                return None

    def get_files(self) -> list[FileModel]:
        log.debug("Retrieving all files")
        with get_db() as db:
            try:
                files = db.query(File).all()
                log.debug(f"Successfully retrieved {len(files)} files")
                return [FileModel.model_validate(file) for file in files]
            except Exception as e:
                log.exception(f"Error retrieving all files: {e}")
                return []

    def get_files_by_ids(self, ids: list[str]) -> list[FileModel]:
        log.debug(f"Retrieving files by ids: {ids}")
        with get_db() as db:
            try:
                files = db.query(File).filter(File.id.in_(ids)).order_by(File.updated_at.desc()).all()
                log.debug(f"Successfully retrieved {len(files)} files out of {len(ids)} requested")
                return [FileModel.model_validate(file) for file in files]
            except Exception as e:
                log.exception(f"Error retrieving files by ids {ids}: {e}")
                return []

    def get_file_metadatas_by_ids(self, ids: list[str]) -> list[FileMetadataResponse]:
        log.debug(f"Retrieving file metadatas by ids: {ids}")
        with get_db() as db:
            try:
                files = db.query(File).filter(File.id.in_(ids)).order_by(File.updated_at.desc()).all()
                log.debug(f"Successfully retrieved {len(files)} file metadatas out of {len(ids)} requested")
                return [
                    FileMetadataResponse(
                        id=file.id,
                        meta=file.meta,
                        created_at=file.created_at,
                        updated_at=file.updated_at,
                    )
                    for file in files
                ]
            except Exception as e:
                log.exception(f"Error retrieving file metadatas by ids {ids}: {e}")
                return []

    def get_files_by_user_id(self, user_id: str) -> list[FileModel]:
        log.debug(f"Retrieving files for user: {user_id}")
        with get_db() as db:
            try:
                files = db.query(File).filter_by(user_id=user_id).all()
                log.debug(f"Successfully retrieved {len(files)} files for user {user_id}")
                return [FileModel.model_validate(file) for file in files]
            except Exception as e:
                log.exception(f"Error retrieving files for user {user_id}: {e}")
                return []

    def update_file_hash_by_id(self, id: str, hash: str) -> Optional[FileModel]:
        log.info(f"Updating file hash for file {id} to {hash}")
        with get_db() as db:
            try:
                file = db.query(File).filter_by(id=id).first()
                if file:
                    file.hash = hash
                    file.updated_at = int(time.time())
                    db.commit()
                    log.info(f"Successfully updated file hash for {id}")
                    return FileModel.model_validate(file)
                else:
                    log.warning(f"File not found for hash update: {id}")
                    return None
            except Exception as e:
                log.exception(f"Error updating file hash for {id}: {e}")
                return None

    def update_file_data_by_id(self, id: str, data: dict) -> Optional[FileModel]:
        log.info(f"Updating file data for file {id} with keys: {list(data.keys())}")
        with get_db() as db:
            try:
                file = db.query(File).filter_by(id=id).first()
                if file:
                    file.data = {**(file.data if file.data else {}), **data}
                    file.updated_at = int(time.time())
                    db.commit()
                    log.info(f"Successfully updated file data for {id}")
                    return FileModel.model_validate(file)
                else:
                    log.warning(f"File not found for data update: {id}")
                    return None
            except Exception as e:
                log.exception(f"Error updating file data for {id}: {e}")
                return None

    def update_file_metadata_by_id(self, id: str, meta: dict) -> Optional[FileModel]:
        log.info(f"Updating file metadata for file {id} with keys: {list(meta.keys())}")
        with get_db() as db:
            try:
                file = db.query(File).filter_by(id=id).first()
                if file:
                    file.meta = {**(file.meta if file.meta else {}), **meta}
                    file.updated_at = int(time.time())
                    db.commit()
                    log.info(f"Successfully updated file metadata for {id}")
                    return FileModel.model_validate(file)
                else:
                    log.warning(f"File not found for metadata update: {id}")
                    return None
            except Exception as e:
                log.exception(f"Error updating file metadata for {id}: {e}")
                return None

    def delete_file_by_id(self, id: str) -> bool:
        log.info(f"Deleting file by id: {id}")
        with get_db() as db:
            try:
                result = db.query(File).filter_by(id=id).delete()
                db.commit()
                if result > 0:
                    log.info(f"Successfully deleted file {id}")
                    return True
                else:
                    log.warning(f"File not found for deletion: {id}")
                    return False
            except Exception as e:
                log.exception(f"Error deleting file {id}: {e}")
                return False

    def delete_all_files(self) -> bool:
        log.warning("Deleting all files from database")
        with get_db() as db:
            try:
                result = db.query(File).delete()
                db.commit()
                log.warning(f"Successfully deleted {result} files from database")
                return True
            except Exception as e:
                log.exception(f"Error deleting all files: {e}")
                return False


Files = FilesTable()
