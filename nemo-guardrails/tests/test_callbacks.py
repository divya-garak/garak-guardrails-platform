# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from uuid import uuid4

import pytest
from langchain.schema import Generation, LLMResult
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration

from nemoguardrails.context import explain_info_var, llm_call_info_var, llm_stats_var
from nemoguardrails.logging.callbacks import LoggingCallbackHandler
from nemoguardrails.logging.explain import ExplainInfo, LLMCallInfo
from nemoguardrails.logging.stats import LLMStats


@pytest.mark.asyncio
async def test_token_usage_tracking_with_usage_metadata():
    """Test that token usage is tracked when usage_metadata is available (stream_usage=True scenario)."""

    llm_call_info = LLMCallInfo()
    llm_call_info_var.set(llm_call_info)

    llm_stats = LLMStats()
    llm_stats_var.set(llm_stats)

    explain_info = ExplainInfo()
    explain_info_var.set(explain_info)

    handler = LoggingCallbackHandler()

    # simulate the LLM response with usage metadata (as would happen with stream_usage=True)
    ai_message = AIMessage(
        content="Hello! How can I help you?",
        usage_metadata={"input_tokens": 10, "output_tokens": 6, "total_tokens": 16},
    )

    chat_generation = ChatGeneration(message=ai_message)
    llm_result = LLMResult(generations=[[chat_generation]])

    # call the on_llm_end method
    await handler.on_llm_end(llm_result, run_id=uuid4())

    assert llm_call_info.total_tokens == 16
    assert llm_call_info.prompt_tokens == 10
    assert llm_call_info.completion_tokens == 6

    assert llm_stats.get_stat("total_tokens") == 16
    assert llm_stats.get_stat("total_prompt_tokens") == 10
    assert llm_stats.get_stat("total_completion_tokens") == 6


@pytest.mark.asyncio
async def test_token_usage_tracking_with_llm_output_fallback():
    """Test token usage tracking with legacy llm_output format."""

    llm_call_info = LLMCallInfo()
    llm_call_info_var.set(llm_call_info)

    llm_stats = LLMStats()
    llm_stats_var.set(llm_stats)

    explain_info = ExplainInfo()
    explain_info_var.set(explain_info)

    handler = LoggingCallbackHandler()

    # simulate LLM response with token usage in llm_output (fallback scenario)
    generation = Generation(text="Fallback response")
    llm_result = LLMResult(
        generations=[[generation]],
        llm_output={
            "token_usage": {
                "total_tokens": 20,
                "prompt_tokens": 12,
                "completion_tokens": 8,
            }
        },
    )

    await handler.on_llm_end(llm_result, run_id=uuid4())

    assert llm_call_info.total_tokens == 20
    assert llm_call_info.prompt_tokens == 12
    assert llm_call_info.completion_tokens == 8

    assert llm_stats.get_stat("total_tokens") == 20
    assert llm_stats.get_stat("total_prompt_tokens") == 12
    assert llm_stats.get_stat("total_completion_tokens") == 8


@pytest.mark.asyncio
async def test_no_token_usage_tracking_without_metadata():
    """Test that no token usage is tracked when metadata is not available."""

    llm_call_info = LLMCallInfo()
    llm_call_info_var.set(llm_call_info)

    llm_stats = LLMStats()
    llm_stats_var.set(llm_stats)

    explain_info = ExplainInfo()
    explain_info_var.set(explain_info)

    handler = LoggingCallbackHandler()

    # simulate LLM response without usage metadata (stream_usage=False scenario)
    ai_message = AIMessage(content="Hello! How can I help you?")
    chat_generation = ChatGeneration(message=ai_message)
    llm_result = LLMResult(generations=[[chat_generation]])

    await handler.on_llm_end(llm_result, run_id=uuid4())

    assert llm_call_info.total_tokens is None or llm_call_info.total_tokens == 0
    assert llm_call_info.prompt_tokens is None or llm_call_info.prompt_tokens == 0
    assert (
        llm_call_info.completion_tokens is None or llm_call_info.completion_tokens == 0
    )


@pytest.mark.asyncio
async def test_multiple_generations_token_accumulation():
    """Test that token usage accumulates across multiple generations."""

    llm_call_info = LLMCallInfo()
    llm_call_info_var.set(llm_call_info)

    llm_stats = LLMStats()
    llm_stats_var.set(llm_stats)

    explain_info = ExplainInfo()
    explain_info_var.set(explain_info)

    handler = LoggingCallbackHandler()

    ai_message1 = AIMessage(
        content="First response",
        usage_metadata={"input_tokens": 5, "output_tokens": 3, "total_tokens": 8},
    )

    ai_message2 = AIMessage(
        content="Second response",
        usage_metadata={"input_tokens": 7, "output_tokens": 4, "total_tokens": 11},
    )

    chat_generation1 = ChatGeneration(message=ai_message1)
    chat_generation2 = ChatGeneration(message=ai_message2)
    llm_result = LLMResult(generations=[[chat_generation1, chat_generation2]])

    await handler.on_llm_end(llm_result, run_id=uuid4())

    assert llm_call_info.total_tokens == 19  # 8 + 11
    assert llm_call_info.prompt_tokens == 12  # 5 + 7
    assert llm_call_info.completion_tokens == 7  # 3 + 4

    assert llm_stats.get_stat("total_tokens") == 19
    assert llm_stats.get_stat("total_prompt_tokens") == 12
    assert llm_stats.get_stat("total_completion_tokens") == 7
