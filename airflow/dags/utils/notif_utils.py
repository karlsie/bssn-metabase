def construct_failure_message(context):
    """Construct Slack message payload for DAG failure notification.
    
    Args:
        context: Airflow task context dictionary
        
    Returns:
        dict: Slack message payload with blocks
    """
    ti = context['ti']
    dag_id = ti.dag_id
    run_id = ti.run_id
    task_id = ti.task_id
    start_date = ti.start_date.strftime("%Y-%m-%d %H:%M:%S") if ti.start_date else "N/A"
    end_date = ti.end_date.strftime("%Y-%m-%d %H:%M:%S") if ti.end_date else "N/A"
    exception = context.get('exception')
    
    return {
        "text": "🚨 Airflow DAG Failure Alert",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 DAG Failure Alert"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*DAG ID:*\n{dag_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Start Date:*\n{start_date}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Task ID:*\n{task_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*End Date:*\n{end_date}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Run ID:*\n{run_id}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Exception:*\n```{str(exception)[:500]}```"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Please check the Airflow UI for more details."
                }
            }
        ]
    }
