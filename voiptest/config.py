"""Configuration models for VoIP test specifications using Pydantic."""

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


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
    """Account information - flexible dict of named accounts."""
    
    model_config = ConfigDict(extra='allow')
    
    # At minimum, allow dynamic accounts
    caller: Optional[Account] = Field(None, description="Calling party account (optional)")
    callee: Optional[Account] = Field(None, description="Called party account (optional)")
    
    def __getattr__(self, name: str) -> Optional[Account]:
        """Allow accessing accounts by name."""
        try:
            return super().__getattribute__(name)
        except AttributeError:
            # Try to get from model data
            if name in self.__dict__:
                return self.__dict__[name]
            # Return None for missing accounts
            return None


class Call(BaseModel):
    """Call parameters."""

    from_: str = Field(..., alias="from", description="Caller account key (e.g., 'caller')")
    to: str = Field(..., description="Callee account key or literal destination (e.g., 'callee' or '2000')")
    timeout_s: int = Field(30, description="Maximum time to wait for call setup (seconds)")
    max_duration_s: int = Field(60, description="Maximum call duration (seconds)")


class Expect(BaseModel):
    """Expected call outcome."""

    outcome: Literal["answered", "failed", "busy", "no_answer"] = Field(
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

    version: int = Field(1, description="Config schema version")
    name: str = Field(..., description="Test scenario name")
    target: Target = Field(..., description="Target VoIP server")
    accounts: Accounts = Field(..., description="Test accounts")
    call: Call = Field(..., description="Call parameters")
    expect: Expect = Field(..., description="Expected outcome")
    matrix: Optional[Matrix] = Field(None, description="Matrix expansion for multiple targets")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
