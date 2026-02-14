import sys
import os
import time

# Ensure we can import kibo_core
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from kibo_core.infrastructure.memory import KiboMemory
from kibo_core.domain.blueprint import AgentConfig
from kibo_core.infrastructure.interfaces.client import KiboAgent
from rich.console import Console
from rich.markdown import Markdown

console = Console()


def main():
    console.print("[bold blue]🤖 Kibo AI - Memory Enhanced Chat Agent[/bold blue]")
    console.print("[dim]Powered by Kibo Core, Agno, and Mem0[/dim]\n")

    # 1. Initialize Memory
    try:
        memory = KiboMemory()
        # Test connection (will throw if DB not running)
        memory.search("health check", user_id="system")
        console.print("[green]✅ Memory Layer (Mem0 + ChromaDB) connected.[/green]")
    except Exception as e:
        console.print("[bold red]❌ Failed to connect to Memory Layer.[/bold red]")
        console.print(f"Error: {e}")
        console.print(
            "\n[yellow]Tip: Please run 'kibo start db' in a separate terminal.[/yellow]"
        )
        return

    # 2. Configure Agent
    console.print("[yellow]🔄 Initializing Agent...[/yellow]")

    # We use Agno as the engine
    blueprint = AgentConfig(
        name="kibo-memory-agent",
        description="I am a helpful assistant with long-term memory capabilities.",
        instructions="""
        You are an intelligent assistant.
        Always answer the user's questions helpfully.
        You have access to a long-term memory system.
        When providing answers, refer to context provided in the 'System Note' if relevant.
        Be concise but friendly.
        """,
        agent="agno",
        model="gpt-4o-mini",  # Uses Proxy mapping
        distributed=False,  # Run locally to maintain state easily in this loop
    )

    try:
        agent = KiboAgent(config=blueprint)
        console.print("[green]✅ Agent initialized.[/green]\n")
    except Exception as e:
        console.print(f"[bold red]❌ Failed to initialize Agent: {e}[/bold red]")
        return

    console.print(
        "[bold]💬 Chat Session Started (type 'exit' or 'quit' to stop)[/bold]"
    )
    console.print("-" * 50)

    user_id = "console_user"

    while True:
        try:
            user_input = console.input("[bold green]You > [/bold green]").strip()
        except KeyboardInterrupt:
            break

        if user_input.lower() in ["exit", "quit"]:
            console.print("[blue]Goodbye! 👋[/blue]")
            break

        if not user_input:
            continue

        # 3. Retrieve Context from Memory
        related_memories = []
        try:
            results = memory.search(user_input, user_id=user_id, limit=3)
            # Normalize results structure
            if isinstance(results, dict) and "results" in results:
                related_memories = [m.get("memory", "") for m in results["results"]]
            elif isinstance(results, list):
                related_memories = [m.get("memory", "") for m in results]
        except Exception as e:
            console.print(f"[red]Warning: Memory retrieval failed: {e}[/red]")

        # 4. Construct Prompt with Context
        context_str = ""
        if related_memories:
            console.print(
                f"[dim]🧠 Recall: Found {len(related_memories)} relevant memories.[/dim]"
            )
            context_str = "\n".join(f"- {m}" for m in related_memories)

            # Augment the input for the agent (Simulation of RAG)
            # In a real Kibo RAG pipeline this might be internal, but here we do it explicitly
            augmented_input = f"""
            System Note (Memory Context):
            The following are relevant memories from past interactions with this user:
            {context_str}

            User Query:
            {user_input}
            """
        else:
            augmented_input = user_input

        # 5. Run Agent
        with console.status("[bold blue]Thinking...[/bold blue]"):
            try:
                result = agent.run(augmented_input)
                response_text = result.output_data
            except Exception as e:
                console.print(f"[red]Error during generation: {e}[/red]")
                continue

        # 6. Display Response
        console.print("\n[bold purple]Agent > [/bold purple]", end="")
        console.print(Markdown(response_text))
        console.print()

        # 7. Memorize Interaction
        # We store the raw user input + assistant response
        try:
            memory.add(
                [
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "content": response_text},
                ],
                user_id=user_id,
            )
            # console.print("[dim]💾 Interaction saved to memory.[/dim]")
        except Exception as e:
            console.print(f"[red]Warning: Failed to save memory: {e}[/red]")


if __name__ == "__main__":
    main()
