
read -p "Please enter your Kaggle API token here (e.g. {\"username\":\"corise\",\"key\":\"3536356fgdf\"}): " api_token
echo "Your Kaggle API token is:" $api_token
echo "Installing Kaggle API token to /home/gitpod/.kaggle/kaggle.json (soft-linked to /workspace/kaggle) ..."
echo $api_token > /home/gitpod/.kaggle/kaggle.json
echo "Successfully installed."

chmod 600 /home/gitpod/.kaggle/kaggle.json
