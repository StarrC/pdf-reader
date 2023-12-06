import os
import openai
import time
from openai import OpenAI
import time
 
openai.api_key = os.environ["OPENAI_API_KEY"]

start_time = time.time()

client = OpenAI()

async def questionText(prompt):
    return input(prompt)

async def main():
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
            "What is the main topic of the uploaded file?",
            "Can you summarize the key points discussed in the file?",
            "Are there any notable conclusions or findings in the file?"
        ]

        # Asking predefined questions
        for question in predefined_questions:
            print(f"\nQuestion: {question}")

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

            # If an assistant message is found, print it
            if last_message_for_run:
                print(f"Response: {last_message_for_run.content} \n")

        # Then ask if the user has any more questions about the uploaded file
        continue_asking = await questionText("Do you have any more questions about the uploaded file? (yes/no) ")
        if continue_asking.lower() == "yes":
            additional_question = await questionText("\nWhat is your additional question about the file? ")
            # [Process the additional question in a similar way as above]
            # ... [You can replicate the code used to process each predefined question]

        print("Thank you, hope all your questions are solved!\n")

    except Exception as e:
        print(f"An error occurred: {e}")

    await main()
    
    print("Process finished --- %s seconds ---" % (time.time() - start_time))

