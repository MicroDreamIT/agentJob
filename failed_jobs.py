# # get input
# from selenium import webdriver
# from sqlalchemy.orm import sessionmaker, Session
#
# from core.database import Job, engine, FailedJob
# from job_sites.seek.apply_on_job import apply_on_job
# from job_sites.seek.login import login_to_seek
# from job_sites.seek.search_jobs import search_jobs
# from sqlalchemy import select
#
# if __name__ == "__main__":
#     # Perform the query
#
#     # logged_in_driver = login_to_seek()
#     logged_in_driver = login_to_seek()
#     if logged_in_driver:
#         session = Session(engine)
#
#         not_quick_applies = select(Job).where(Job.is_quick_apply == 0)
#
#         for fail_job in session.scalars(not_quick_applies):
#             print(f"➡️Processing job: {fail_job.link}, job_id: {fail_job.provider_id}")
#             logged_in_driver.get(fail_job.link)
#             logged_in_driver.get(
#                 'https://www.seek.com.au/job/82917147/apply/role-requirements?sol=0c58f7151b4c526d7e0a8ba11f2db9ff1b81f5df')
#             # job_detail_returns = apply_on_job(driver, '82897618')
#             success_if = apply_step_1_resume_cover_letter(driver, cover_letter)
#             if success_if:
#                 apply_step_2_employer_questions(driver)
#
#             try:
#                 session.commit()
#             except Exception as e:
#                 print(f"Error applying for job: {e}")
#                 stmt = select(FailedJob).where(FailedJob.provider_id == fail_job.provider_id)
#                 failed_job_is_exist = session.scalars(stmt).one()
#                 if not failed_job_is_exist:
#                     failed_job_save = FailedJob(
#                         provider='SEEK',
#                         provider_id=fail_job.provider_id,
#                         link=fail_job.link,
#                         error_message=str(e)
#                     )
#                     session.add(failed_job_save)
#                     session.commit()
#         # Close the session
#         session.close()
