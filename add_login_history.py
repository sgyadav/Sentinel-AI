import sys

with open('backend/models.py', 'r') as f:
    content = f.read()

# Add LoginHistoryDB before the Pydantic models section
login_history_model = """

class LoginHistoryDB(Base):
    __tablename__ = "login_history"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), nullable=False, index=True)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    logout_time = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=False)
    status = Column(String(50), nullable=False)
    reason = Column(String(255), nullable=True)
    session_duration = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
"""

# Find the insertion point (right before the Pydantic models section)
insertion_point = content.find('# ============= PYDANTIC MODELS')
if insertion_point > 0:
    new_content = content[:insertion_point] + login_history_model + '\n' + content[insertion_point:]
    with open('backend/models.py', 'w') as f:
        f.write(new_content)
    print('LoginHistoryDB model added')
else:
    print('Could not find insertion point')
