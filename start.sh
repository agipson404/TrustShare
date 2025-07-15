# Start backend in a new terminal tab or window
echo "Starting backend..."
gnome-terminal -- bash -c "cd /home/kali/Desktop/trustshare/backend && source venv/bin/activate && uvicorn main:app --reload; exec bash"

# Wait a few seconds for backend to initialize
sleep 5

# Start frontend
echo "Starting frontend..."
cd /home/kali/Desktop/trustshare/frontend
npm start
