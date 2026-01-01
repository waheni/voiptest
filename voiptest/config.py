"""Configuration models for VoIP test specifications using Pydantic."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Target(BaseModel):
    """VoIP target server configuration."""

    host: str = Field(..., description="Target host/IP address")
    port: int = Field(5060, description="Target SIP port")
    transport: Literal["udp", "tcp", "tls"] = Field("udp", description="Transport protocol")
    domain: Optional[str] = Field(None, description="SIP domain")


class Account(BaseModel):
    """SIP account credentials."""

    username: str = Field(..., description="SIP username/extension")
    password: str = Field(..., description="SIP password")
    display_name: Optional[str] = Field(None, description="Display name for caller ID")


class Accounts(BaseModel):
    """Caller and callee account information."""

    caller: Account = Field(..., description="Calling party account")
    callee: Account = Field(..., description="Called party account")


class Call(BaseModel):
    """Call parameters."""

    from_: str = Field(..., alias="from", description="Caller SIP URI or extension")
    to: str = Field(..., description="Callee SIP URI or extension")
    timeout_s: int = Field(30, description="Maximum time to wait for call setup (seconds)")
    max_duration_s: int = Field(60, description="Maximum call duration (seconds)")


class Expect(BaseModel):
    """Expected call outcome."""

    outcome: Literal["success", "failure", "busy", "timeout"] = Field(
        ..., description="Expected call outcome"
    )
    final_sip_code: Optional[int] = Field(
        None, description="Expected final SIP response code"
    )
    answer_within_s: Optional[int] = Field(
        None, description="Call must be answered within this time (seconds)"
    )
    min_duration_s: Optional[int] = Field(
        None, description="Minimum call duration for success (seconds)"
    )


class Matrix(BaseModel):
    """Matrix expansion configuration for multiple call destinations."""

    to: List[str] = Field(..., description="List of destination URIs/extensions to test")


class VoipTestConfig(BaseModel):
    """Root configuration for a VoIP test scenario."""

    version: str = Field(..., description="Config schema version")
    name: str = Field(..., description="Test scenario name")
    target: Target = Field(..., description="Target VoIP server")
    accounts: Accounts = Field(..., description="Test accounts")
    call: Call = Field(..., description="Call parameters")
    expect: Expect = Field(..., description="Expected outcome")
    matrix: Optional[Matrix] = Field(None, description="Matrix expansion for multiple targets")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
