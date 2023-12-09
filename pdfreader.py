import os
import openai
import time
from openai import OpenAI
 
openai.api_key = os.environ["OPENAI_API_KEY"]

start_time = time.time()

client = OpenAI()

async def questionText(prompt):
    return input(prompt)

async def main():
    responses = []  # Initialize responses list at the start of the main function

    try:
        # Upload a file with an "assistants" purpose
        file = client.files.create(
            file=open("fair_model.pdf", "rb"),
            purpose='assistants'
        )
        assistant = client.beta.assistants.create(
            name="Researcher",
            instructions="You are a customer support chatbot. Use your knowledge base to best respond to customer queries.",
            model="gpt-4-1106-preview",
            tools=[{"type": "retrieval"}],
            file_ids=[file.id]
        )

        # Create a thread
        thread = client.beta.threads.create()

        # Predefined questions about the uploaded file
        predefined_questions = [
            "What is the title of the uploaded file?",
            "Summarize the math equations discovered in the file into a bullet point list and convert the equations into plain text. Then, summarize how to solve the equation."
        ]

        # Asking predefined questions and collecting responses
        for question in predefined_questions:
            # Pass in the predefined question into the existing thread
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=question
            )

            # Use runs to wait for the assistant response and then retrieve it
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )

            # Polling mechanism to check if run is completed
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            while run_status.status != "completed":
                time.sleep(2)
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

            # Get the last assistant message from the messages array
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            last_message_for_run = next(
                (msg for msg in reversed(messages.data) if msg.run_id == run.id and msg.role == "assistant"),
                None
            )

            # If an assistant message is found, process its content
            if last_message_for_run:
                for content in last_message_for_run.content:
                    # Check if the content is of type 'text'
                    if hasattr(content, 'text') and content.type == 'text':
                        # Append the text value to the responses list
                        responses.append(f"Question: {question}\nResponse: {content.text.value} \n")
                        break  # Break after finding the first text content

        # Print responses to predefined questions
        print("\nResponses to Predefined Questions:")
        for response in responses:
            print(response)

        # Loop for additional questions
        while True:
            continue_asking = await questionText("Do you have any more questions about the uploaded file? (yes/no) ")
            if continue_asking.lower() != "yes":
                break

            additional_question = await questionText("What is your additional question about the file? ")

            # Process the additional question
            client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=additional_question
            )

            # Use runs to wait for the assistant response and then retrieve it
            run = client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant.id
            )

            # Polling mechanism to check if run is completed
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            while run_status.status != "completed":
                time.sleep(2)
                run_status = client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

            # Get the last assistant message for the additional question
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            last_message_for_run = next(
                (msg for msg in reversed(messages.data) if msg.run_id == run.id and msg.role == "assistant"),
                None
            )

            # If an assistant message is found, process its content
            if last_message_for_run:
                for content in last_message_for_run.content:
                    if hasattr(content, 'text') and content.type == 'text':
                        print(f"\nAdditional Question: {additional_question}\nResponse: {content.text.value} \n")
                        break

        print("Thank you and have a nice day!\n")

    except Exception as e:
        print(f"An error occurred: {e}")

    await main()