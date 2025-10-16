"""
Simple Chat Bot using Azure AI Foundry SDK
This chat bot uses Azure AI Projects with agents, threads, and messages functionality.
"""

import os
import time
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AzureAIFoundryBot:
    """
    Chat bot implementation using Azure AI Foundry SDK with agents and threads
    """
    
    def __init__(self):
        """Initialize the Azure AI Foundry client with authentication"""
        # Load environment variables
        load_dotenv()
        
        # Get configuration from environment variables
        self.project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT")
        
        if not self.project_endpoint:
            raise ValueError("AZURE_AI_PROJECT_ENDPOINT environment variable is required")
        
        # Use DefaultAzureCredential for secure authentication
        # This supports managed identity, service principal, and interactive browser flows
        try:
            credential = DefaultAzureCredential()
            
            # Initialize the AI Project client using endpoint string
            self.client = AIProjectClient.from_endpoint(
                endpoint=self.project_endpoint,
                credential=credential
            )
            logger.info("Successfully initialized Azure AI Foundry client")
            
        except Exception as e:
            logger.error(f"Failed to initialize Azure AI Foundry client: {e}")
            raise
        
        # Initialize agent and thread
        self.agent = None
        self.thread = None
        self._initialize_agent_and_thread()
    
    def _initialize_agent_and_thread(self):
        """Initialize the AI agent and conversation thread"""
        try:
            # Create or get an agent
            # You can customize the agent with specific instructions and models
            self.agent = self.client.agents.create_agent(
                model="gpt-4",  # Specify the model you want to use
                name="ChatBot Assistant",
                instructions="You are a helpful AI assistant. Provide clear, concise, and helpful responses to user questions.",
                tools=[]  # Add tools if needed
            )
            logger.info(f"Created agent: {self.agent.id}")
            
            # Create a new thread for the conversation
            self.thread = self.client.agents.create_thread()
            logger.info(f"Created thread: {self.thread.id}")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent and thread: {e}")
            raise
    
    def send_message(self, user_message: str) -> str:
        """
        Send a message to the chat bot and get a response
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: The bot's response
        """
        try:
            # Add the user's message to the thread
            message = self.client.agents.create_message(
                thread_id=self.thread.id,
                role="user",
                content=user_message
            )
            logger.info(f"Added user message: {message.id}")
            
            # Run the agent on the thread
            run = self.client.agents.create_run(
                thread_id=self.thread.id,
                agent_id=self.agent.id
            )
            logger.info(f"Started run: {run.id}")
            
            # Wait for the run to complete
            backoff = 1  # initial backoff in seconds
            max_backoff = 8  # maximum backoff in seconds
            while run.status in ["queued", "in_progress", "cancelling"]:
                time.sleep(backoff)
                run = self.client.agents.get_run(
                    thread_id=self.thread.id,
                    run_id=run.id
                )
                if backoff < max_backoff:
                    backoff = min(backoff * 2, max_backoff)
            
            if run.status == "completed":
                # Get the latest messages from the thread
                messages = self.client.agents.list_messages(thread_id=self.thread.id)
                
                # Find the assistant's response (most recent message from assistant)
                # Sort messages by created_at descending to ensure most recent first
                sorted_messages = sorted(messages.data, key=lambda m: m.created_at, reverse=True)
                for msg in sorted_messages:
                    if msg.role == "assistant":
                        # Extract text content from the message
                        if msg.content and len(msg.content) > 0:
                            return msg.content[0].text.value
                            break
                
                return "I apologize, but I couldn't generate a response."
            
            else:
                logger.error(f"Run failed with status: {run.status}")
                return f"Sorry, there was an error processing your request. Status: {run.status}"
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return f"Sorry, there was an error: {str(e)}"
    
    def get_conversation_history(self) -> list:
        """
        Get the conversation history from the current thread
        
        Returns:
            list: List of messages in the conversation
        """
        try:
            messages = self.client.agents.list_messages(thread_id=self.thread.id)
            conversation = []
            
            for message in reversed(messages.data):
                role = message.role
                content = ""
                if message.content and len(message.content) > 0:
                    content = message.content[0].text.value
                
                conversation.append({
                    "role": role,
                    "content": content,
                    "timestamp": message.created_at
                })
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    def reset_conversation(self):
        """Reset the conversation by creating a new thread"""
        try:
            self.thread = self.client.agents.create_thread()
            logger.info(f"Reset conversation with new thread: {self.thread.id}")
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}")


def main():
    """Main function to run the chat bot"""
    print("🤖 Azure AI Foundry Chat Bot")
    print("Type 'quit' to exit, 'reset' to start a new conversation, or 'history' to see conversation history")
    print("-" * 50)
    
    try:
        # Initialize the chat bot
        bot = AzureAIFoundryBot()
        print("✅ Chat bot initialized successfully!")
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() == 'quit':
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'reset':
                bot.reset_conversation()
                print("🔄 Conversation reset!")
                continue
            elif user_input.lower() == 'history':
                history = bot.get_conversation_history()
                print("\n📜 Conversation History:")
                for msg in history:
                    role_emoji = "🤖" if msg["role"] == "assistant" else "👤"
                    print(f"{role_emoji} {msg['role'].title()}: {msg['content']}")
                continue
            
            if not user_input:
                continue
            
            # Send message and get response
            print("🤖 Bot: ", end="", flush=True)
            response = bot.send_message(user_input)
            print(response)
            
    except Exception as e:
        logger.error(f"Failed to initialize chat bot: {e}")
        print(f"❌ Error: {e}")
        print("Please check your Azure AI Foundry configuration and try again.")


if __name__ == "__main__":
    main()