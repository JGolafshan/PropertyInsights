#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Date: 07/02/2025
Author: Joshua David Golafshan
"""

from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timezone
from src.backend.property_pydantic_model import Property
from beanie import (Document, Insert, Replace, SaveChanges, Update, before_event)


class AuditBase(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    class Settings:
        abstract = True

    @before_event(Insert)
    async def set_created_at(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
            self.created_by = "ScaperAutomation"

    @before_event(Update, SaveChanges, Replace)
    async def set_updated_at(self):
        self.updated_at = datetime.now(timezone.utc)
        self.updated_by = "ScaperAutomation"

    async def soft_delete(self, updated_by: Optional[str] = None):
        self.deleted_at = datetime.now(timezone.utc)
        self.updated_by = updated_by
        await self.save()



class PropertyDocument(Property, AuditBase, Document):

    class Settings:
        name = "property"

