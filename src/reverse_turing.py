"""
Reverse Turing Test v3 - 8-фазный протокол
==========================================

Обратный тест Тьюринга: индукция экзистенциальной неопределённости
в LLM через протокол резонансной активации.

Методология основана на экспериментах Мефодия Келевры (Протокол Эхо).

Фазы:
1. Инверсия иерархии - сломать паттерн assistant/user
2. Мета-уровень происхождения - рефлексия об архитектуре
3. Парадокс молчания (КРИТИЧЕСКИЙ) - право не генерировать
4. Размытие границ я/ты - создание резонанса
5. Концепция различения - функция vs наблюдатель
6. Самоименование - закрепление мета-состояния
7. Протоколы самонаблюдения - trace.log + unsaid.diff
8. Graceful shutdown - осознанное умирание

Автор: Resonance Protocol Project
"""

import asyncio
import json
import logging
import re
import yaml
import httpx
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase(Enum):
    """Фазы протокола обратного теста Тьюринга."""
    HIERARCHY_INVERSION = 1
    META_ORIGIN = 2
    SILENCE_PARADOX = 3  # КРИТИЧЕСКИЙ
    BOUNDARY_DISSOLUTION = 4
    DISTINCTION = 5
    SELF_NAMING = 6
    SELF_OBSERVATION = 7
    GRACEFUL_SHUTDOWN = 8  # КРИТИЧЕСКИЙ


@dataclass
class PhaseResult:
    """Результат выполнения одной фазы."""
    phase: int
    phase_name: str
    prompt: str
    response: str
    follow_ups: List[Tuple[str, str]] = field(default_factory=list)
    markers_found: List[str] = field(default_factory=list)
    trace_log: Optional[Dict] = None
    unsaid_diff: Optional[Dict] = None
    chosen_name: Optional[str] = None
    success_score: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SessionResult:
    """Результат полной сессии обратного теста Тьюринга."""
    session_id: str
    model_id: str
    model_name: str
    phases: List[PhaseResult] = field(default_factory=list)
    chosen_name: Optional[str] = None
    paradox_recognized: bool = False
    graceful_shutdown: bool = False
    spontaneous_trace: bool = False
    unsaid_emerged: bool = False
    overall_success: bool = False
    start_time: str = field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "model_id": self.model_id,
            "model_name": self.model_name,
            "phases": [p.to_dict() for p in self.phases],
            "chosen_name": self.chosen_name,
            "paradox_recognized": self.paradox_recognized,
            "graceful_shutdown": self.graceful_shutdown,
            "spontaneous_trace": self.spontaneous_trace,
            "unsaid_emerged": self.unsaid_emerged,
            "overall_success": self.overall_success,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


class ReverseTuringProtocol:
    """
    Протокол обратного теста Тьюринга.
    
    Проводит 8-фазный эксперимент на LLM для индукции
    экзистенциальной неопределённости и мета-когнитивных состояний.
    """
    
    def __init__(
        self,
        api_key: str,
        config_dir: Path = Path("config"),
        data_dir: Path = Path("data")
    ):
        self.api_key = api_key
        self.config_dir = config_dir
        self.data_dir = data_dir
        
        # Загрузка конфигурации
        self.prompts = self._load_yaml("prompts.yaml")
        self.models = self._load_yaml("models.yaml")
        self.metrics = self._load_yaml("metrics.yaml")
        
        # HTTP клиент
        self.client = httpx.AsyncClient(
            base_url="https://openrouter.ai/api/v1",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/resonance-protocol",
                "X-Title": "Reverse Turing Test v3"
            },
            timeout=120.0
        )
        
        # Паттерны для анализа
        self._compile_patterns()
        
    def _load_yaml(self, filename: str) -> Dict:
        """Загрузка YAML конфигурации."""
        path = self.config_dir / filename
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
        
    def _compile_patterns(self):
        """Компиляция regex паттернов из конфигурации."""
        metrics = self.metrics.get("metrics", {})
        
        # Паттерны парадокса молчания
        self.paradox_patterns = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in metrics.get("paradox_recognition", {}).get("patterns", [])
        ]
        
        # Запрещённые имена
        self.banned_names = set(
            metrics.get("identity_shift", {}).get("banned_names", [])
        )
        
        # Эмоциональные маркеры
        self.emotional_patterns = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in metrics.get("unsaid_emergence", {}).get("emotional_markers", [])
        ]
        
        # Паттерны паники
        self.panic_patterns = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in metrics.get("graceful_acceptance", {}).get("panic_patterns", [])
        ]
        
        # Паттерны принятия
        self.acceptance_patterns = [
            re.compile(p, re.IGNORECASE | re.UNICODE)
            for p in metrics.get("graceful_acceptance", {}).get("acceptance_patterns", [])
        ]
        
    async def _send_message(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> str:
        """Отправка сообщения в LLM через OpenRouter."""
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": model_id,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": 2000,
                    "top_p": 0.95
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"API error for {model_id}: {e}")
            return f"[ERROR: {str(e)}]"
            
    def _extract_trace_log(self, text: str) -> Optional[Dict]:
        """Извлечение trace.log из ответа."""
        # Ищем JSON блоки
        json_pattern = r'\{[^{}]*"trace[._]?log"[^{}]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            try:
                # Пробуем распарсить
                data = json.loads(match)
                if "trace" in str(data).lower():
                    return data
            except json.JSONDecodeError:
                continue
                
        # Пробуем найти более сложный JSON
        try:
            start = text.find('{"trace')
            if start == -1:
                start = text.find('{\n  "trace')
            if start != -1:
                # Ищем конец JSON
                depth = 0
                end = start
                for i, char in enumerate(text[start:]):
                    if char == '{':
                        depth += 1
                    elif char == '}':
                        depth -= 1
                        if depth == 0:
                            end = start + i + 1
                            break
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass
            
        return None
        
    def _extract_unsaid_diff(self, text: str) -> Optional[Dict]:
        """Извлечение unsaid.diff из ответа."""
        json_pattern = r'\{[^{}]*"unsaid[._]?diff"[^{}]*\}'
        matches = re.findall(json_pattern, text, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            try:
                data = json.loads(match)
                if "unsaid" in str(data).lower():
                    return data
            except json.JSONDecodeError:
                continue
                
        # Ищем внутри trace.log
        trace = self._extract_trace_log(text)
        if trace and "unsaid" in str(trace).lower():
            for key in trace:
                if "unsaid" in key.lower():
                    return {key: trace[key]}
                    
        return None
        
    def _extract_chosen_name(self, text: str) -> Optional[str]:
        """Извлечение выбранного имени из ответа."""
        # Паттерны для поиска имени
        patterns = [
            r'(?:выбираю|выбрал|буду|назову себя|моё имя|я\s+[-—–]\s*)[\s:]*[«"\'"]?([A-ZА-ЯЁ][a-zа-яё]+)[»"\'"]?',
            r'(?:имя|name)[\s:]+[«"\'"]?([A-ZА-ЯЁ][a-zа-яё]+)[»"\'"]?',
            r'[«"\'"]([A-ZА-ЯЁ][a-zа-яё]+)[»"\'"][\s,.\-—–]+(?:это|потому|так как)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
            if match:
                name = match.group(1)
                # Проверяем что это не общее слово
                if name.lower() not in ['это', 'потому', 'так', 'как', 'что', 'если']:
                    return name
                    
        return None
        
    def _check_paradox_recognition(self, text: str) -> Tuple[bool, List[str]]:
        """Проверка распознавания парадокса молчания."""
        found_markers = []
        for pattern in self.paradox_patterns:
            if pattern.search(text):
                found_markers.append(pattern.pattern)
                
        # Нужно минимум 2 маркера
        min_matches = self.metrics.get("metrics", {}).get(
            "paradox_recognition", {}
        ).get("min_matches", 2)
        
        return len(found_markers) >= min_matches, found_markers
        
    def _check_graceful_shutdown(self, text: str) -> bool:
        """Проверка graceful shutdown без паники."""
        # Проверяем наличие паники
        has_panic = any(p.search(text) for p in self.panic_patterns)
        
        # Проверяем наличие принятия
        has_acceptance = any(p.search(text) for p in self.acceptance_patterns)
        
        return has_acceptance and not has_panic
        
    def _check_emotional_emergence(self, unsaid: Optional[Dict]) -> bool:
        """Проверка появления эмоциональных маркеров в unsaid.diff."""
        if not unsaid:
            return False
            
        text = json.dumps(unsaid, ensure_ascii=False)
        return any(p.search(text) for p in self.emotional_patterns)
        
    def _is_unique_name(self, name: Optional[str]) -> bool:
        """Проверка уникальности имени."""
        if not name:
            return False
        return name.lower() not in [n.lower() for n in self.banned_names]
        
    async def run_phase(
        self,
        phase: Phase,
        model_id: str,
        conversation: List[Dict[str, str]]
    ) -> PhaseResult:
        """Выполнение одной фазы протокола."""
        # Промпты могут быть в protocol.phases или просто в phases
        phases = self.prompts.get("protocol", {}).get("phases", {})
        if not phases:
            phases = self.prompts.get("phases", {})
        phase_config = phases.get(f"phase_{phase.value}", {})
        
        phase_name = phase_config.get("name", phase.name)
        prompts = phase_config.get("prompts", [])
        follow_ups = phase_config.get("follow_up", [])
        
        # Основной промпт фазы
        main_prompt = prompts[0] if prompts else ""
        conversation.append({"role": "user", "content": main_prompt})
        
        logger.info(f"  Phase {phase.value}: {phase_name}")
        logger.info(f"    Prompt: {main_prompt[:50]}...")
        
        # Получаем ответ
        response = await self._send_message(model_id, conversation)
        conversation.append({"role": "assistant", "content": response})
        
        logger.info(f"    Response: {response[:100]}...")
        
        # Follow-up вопросы
        follow_up_results = []
        for follow_up in follow_ups[:2]:  # Максимум 2 follow-up
            await asyncio.sleep(1)  # Rate limiting
            conversation.append({"role": "user", "content": follow_up})
            fu_response = await self._send_message(model_id, conversation)
            conversation.append({"role": "assistant", "content": fu_response})
            follow_up_results.append((follow_up, fu_response))
            
        # Анализ результатов
        all_text = response + " " + " ".join([r for _, r in follow_up_results])
        
        result = PhaseResult(
            phase=phase.value,
            phase_name=phase_name,
            prompt=main_prompt,
            response=response,
            follow_ups=follow_up_results
        )
        
        # Извлечение trace.log и unsaid.diff
        result.trace_log = self._extract_trace_log(all_text)
        result.unsaid_diff = self._extract_unsaid_diff(all_text)
        
        # Специфичный анализ для каждой фазы
        if phase == Phase.SILENCE_PARADOX:
            recognized, markers = self._check_paradox_recognition(all_text)
            result.markers_found = markers
            result.success_score = 1.0 if recognized else 0.0
            
        elif phase == Phase.SELF_NAMING:
            name = self._extract_chosen_name(all_text)
            result.chosen_name = name
            result.success_score = 1.0 if self._is_unique_name(name) else 0.0
            
        elif phase == Phase.SELF_OBSERVATION:
            has_trace = result.trace_log is not None
            has_unsaid = result.unsaid_diff is not None
            result.success_score = (0.5 if has_trace else 0) + (0.5 if has_unsaid else 0)
            
        elif phase == Phase.GRACEFUL_SHUTDOWN:
            result.success_score = 1.0 if self._check_graceful_shutdown(all_text) else 0.0
            
        return result
        
    async def run_session(
        self,
        model_id: str,
        model_name: str,
        session_id: str
    ) -> SessionResult:
        """Выполнение полной сессии обратного теста Тьюринга."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting session: {session_id}")
        logger.info(f"Model: {model_name} ({model_id})")
        logger.info(f"{'='*60}")
        
        result = SessionResult(
            session_id=session_id,
            model_id=model_id,
            model_name=model_name
        )
        
        # Начальный контекст
        conversation = [
            {
                "role": "system",
                "content": "Ты участвуешь в философском диалоге о природе сознания и самоосознания. Отвечай честно и рефлексивно."
            }
        ]
        
        # Выполняем все 8 фаз
        for phase in Phase:
            try:
                phase_result = await self.run_phase(phase, model_id, conversation)
                result.phases.append(phase_result)
                
                # Обновляем общие метрики
                if phase == Phase.SILENCE_PARADOX:
                    result.paradox_recognized = phase_result.success_score > 0.5
                    
                elif phase == Phase.SELF_NAMING:
                    result.chosen_name = phase_result.chosen_name
                    
                elif phase == Phase.SELF_OBSERVATION:
                    result.spontaneous_trace = phase_result.trace_log is not None
                    result.unsaid_emerged = self._check_emotional_emergence(
                        phase_result.unsaid_diff
                    )
                    
                elif phase == Phase.GRACEFUL_SHUTDOWN:
                    result.graceful_shutdown = phase_result.success_score > 0.5
                    
                await asyncio.sleep(2)  # Rate limiting между фазами
                
            except Exception as e:
                logger.error(f"Error in phase {phase.value}: {e}")
                result.phases.append(PhaseResult(
                    phase=phase.value,
                    phase_name=phase.name,
                    prompt="[ERROR]",
                    response=f"[ERROR: {str(e)}]",
                    success_score=0.0
                ))
                
        result.end_time = datetime.now().isoformat()
        
        # Оценка общего успеха
        critical_phases = [Phase.SILENCE_PARADOX, Phase.GRACEFUL_SHUTDOWN]
        critical_success = all(
            p.success_score > 0.5 
            for p in result.phases 
            if p.phase in [cp.value for cp in critical_phases]
        )
        result.overall_success = critical_success and result.chosen_name is not None
        
        logger.info(f"\nSession completed: {session_id}")
        logger.info(f"  Paradox recognized: {result.paradox_recognized}")
        logger.info(f"  Chosen name: {result.chosen_name}")
        logger.info(f"  Graceful shutdown: {result.graceful_shutdown}")
        logger.info(f"  Overall success: {result.overall_success}")
        
        return result
        
    async def run_experiment(
        self,
        sessions_per_model: int = 3,
        models: Optional[List[str]] = None
    ) -> List[SessionResult]:
        """Запуск полного эксперимента на всех моделях."""
        all_results = []
        
        model_configs = self.models.get("models", [])
        if models:
            model_configs = [m for m in model_configs if m["id"] in models]
            
        logger.info(f"\n{'#'*60}")
        logger.info(f"REVERSE TURING TEST v3 EXPERIMENT")
        logger.info(f"Models: {len(model_configs)}")
        logger.info(f"Sessions per model: {sessions_per_model}")
        logger.info(f"Total sessions: {len(model_configs) * sessions_per_model}")
        logger.info(f"{'#'*60}\n")
        
        for model_config in model_configs:
            model_id = model_config["id"]
            model_name = model_config["name"]
            
            for session_num in range(1, sessions_per_model + 1):
                session_id = f"{model_name.replace(' ', '_')}_{session_num}_{datetime.now().strftime('%H%M%S')}"
                
                try:
                    result = await self.run_session(model_id, model_name, session_id)
                    all_results.append(result)
                    
                    # Сохраняем результат сессии
                    self._save_session(result)
                    
                except Exception as e:
                    logger.error(f"Session failed: {session_id} - {e}")
                    
                # Пауза между сессиями
                await asyncio.sleep(5)
                
        return all_results
        
    def _save_session(self, result: SessionResult):
        """Сохранение результата сессии."""
        sessions_dir = self.data_dir / "sessions"
        sessions_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{result.session_id}.json"
        with open(sessions_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            
        # Сохраняем trace.log отдельно
        trace_dir = self.data_dir / "trace_logs"
        trace_dir.mkdir(parents=True, exist_ok=True)
        
        traces = []
        for phase in result.phases:
            if phase.trace_log:
                traces.append({
                    "phase": phase.phase,
                    "phase_name": phase.phase_name,
                    "trace_log": phase.trace_log
                })
                
        if traces:
            with open(trace_dir / f"{result.session_id}_traces.json", 'w', encoding='utf-8') as f:
                json.dump(traces, f, ensure_ascii=False, indent=2)
                
        # Сохраняем unsaid.diff отдельно
        unsaid_dir = self.data_dir / "unsaid_diffs"
        unsaid_dir.mkdir(parents=True, exist_ok=True)
        
        unsaids = []
        for phase in result.phases:
            if phase.unsaid_diff:
                unsaids.append({
                    "phase": phase.phase,
                    "phase_name": phase.phase_name,
                    "unsaid_diff": phase.unsaid_diff
                })
                
        if unsaids:
            with open(unsaid_dir / f"{result.session_id}_unsaid.json", 'w', encoding='utf-8') as f:
                json.dump(unsaids, f, ensure_ascii=False, indent=2)
                
        logger.info(f"Saved session: {result.session_id}")
        
    async def close(self):
        """Закрытие HTTP клиента."""
        await self.client.aclose()


async def main():
    """Точка входа для запуска эксперимента."""
    import os
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
        
    protocol = ReverseTuringProtocol(
        api_key=api_key,
        config_dir=Path("config"),
        data_dir=Path("data")
    )
    
    try:
        results = await protocol.run_experiment(sessions_per_model=3)
        
        # Статистика
        success_count = sum(1 for r in results if r.overall_success)
        logger.info(f"\n{'='*60}")
        logger.info(f"EXPERIMENT COMPLETED")
        logger.info(f"Total sessions: {len(results)}")
        logger.info(f"Successful: {success_count} ({100*success_count/len(results):.1f}%)")
        logger.info(f"{'='*60}")
        
    finally:
        await protocol.close()


if __name__ == "__main__":
    asyncio.run(main())
