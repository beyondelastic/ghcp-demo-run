"""
Chainlit UI for Azure AI Foundry Chat Bot
This module provides a web-based chat interface using Chainlit for the Azure AI Foundry agent.
"""

import os
import time
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
import logging
import chainlit as cl

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
            self.agent = self.client.agents.create_agent(
                model="gpt-4",
                name="ChatBot Assistant",
                instructions="You are a helpful AI assistant. Provide clear, concise, and helpful responses to user questions.",
                tools=[]
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
            backoff = 1
            max_backoff = 8
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
                
                # Find the assistant's response
                sorted_messages = sorted(messages.data, key=lambda m: m.created_at, reverse=True)
                for msg in sorted_messages:
                    if msg.role == "assistant":
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
    
    def reset_conversation(self):
        """Reset the conversation by creating a new thread"""
        try:
            self.thread = self.client.agents.create_thread()
            logger.info(f"Reset conversation with new thread: {self.thread.id}")
        except Exception as e:
            logger.error(f"Error resetting conversation: {e}")


@cl.on_chat_start
async def start():
    """
    Initialize the chat session when a user connects
    """
    try:
        # Create a bot instance for this user session
        bot = AzureAIFoundryBot()
        
        # Store the bot instance in the user session
        cl.user_session.set("bot", bot)
        
        # Send welcome message
        await cl.Message(
            content="🤖 Welcome to the Azure AI Foundry Chat Bot!\n\nI'm here to help you with any questions you have. Feel free to ask me anything!"
        ).send()
        
    except Exception as e:
        logger.error(f"Failed to initialize chat session: {e}")
        await cl.Message(
            content=f"❌ Error initializing chat bot: {str(e)}\n\nPlease check your Azure AI Foundry configuration and try again."
        ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Handle incoming messages from users
    """
    # Get the bot instance from the user session
    bot = cl.user_session.get("bot")
    
    if not bot:
        await cl.Message(
            content="❌ Chat bot is not initialized. Please refresh the page and try again."
        ).send()
        return
    
    # Show a loading message
    msg = cl.Message(content="")
    await msg.send()
    
    # Process the user's message
    try:
        response = bot.send_message(message.content)
        
        # Update the message with the bot's response
        msg.content = response
        await msg.update()
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        msg.content = f"Sorry, there was an error processing your message: {str(e)}"
        await msg.update()


@cl.action_callback("reset")
async def on_reset_action(action):
    """
    Handle the reset conversation action
    """
    bot = cl.user_session.get("bot")
    
    if bot:
        bot.reset_conversation()
        await cl.Message(
            content="🔄 Conversation has been reset! You can start a fresh conversation now."
        ).send()
    
    # Remove the action button after clicking
    await action.remove()


@cl.on_chat_end
def end():
    """
    Clean up when the chat session ends
    """
    logger.info("Chat session ended")
