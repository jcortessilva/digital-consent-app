def handle_consent_by_id():
    query_params = st.query_params
    st.write("Debugging: Raw Query Params")
    st.write(query_params)

    if "consent_id" in query_params:
        consent_id = query_params["consent_id"][0]

        # Debugging: Log consent ID from link
        st.write("Debugging: Consent Confirmation")
        st.write(f"Consent ID from Link: {consent_id}")

        try:
            with open(PENDING_CONSENTS_FILE, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Debugging: Log each row being checked
                    st.write(f"Checking Row: {row}")
                    
                    if row["id"] == consent_id:
                        if row["status"] != "pending":
                            st.error("This consent has already been processed.")
                            return True
                        
                        # Display consent details
                        st.subheader("Consent Details")
                        st.write(f"Initiator: {row['initiator']}")
                        st.write(f"Other Party: {row['other_party_email']}")
                        st.write(f"Details: {row['details']}")
                        st.write(f"Validity: {row['validity']}")

                        # Add options to confirm or reject
                        col1, col2 = st.columns(2)
                        if col1.button("Confirm Consent"):
                            update_consent_status(consent_id, "confirmed")
                            st.success("Consent confirmed successfully!")
                            notify_initiator(row['initiator'], "confirmed")
                        if col2.button("Reject Consent"):
                            update_consent_status(consent_id, "rejected")
                            st.warning("Consent rejected.")
                            notify_initiator(row['initiator'], "rejected")
                        return True

            st.error("Consent not found.")
        except FileNotFoundError:
            st.error("Pending consents file not found.")
        except Exception as e:
            st.error(f"Error handling consent: {e}")
        return True
    return False






