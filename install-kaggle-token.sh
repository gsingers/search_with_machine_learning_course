mkdir -p home/gitpod/.kaggle
read -p "Please enter your Kaggle API token here (e.g. {\"username\":\"corise\",\"key\":\"6ebf9bb14dde51cf09aca7604de762ak\"})" api_token
echo "Your Kaggle API token is:" $api_token
echo "Installing Kaggle API token to /home/gitpod/.kaggle/kaggle.json ..."
echo $api_token > /home/gitpod/.kaggle/kaggle.json
echo "Successfully installed. The token is also persisted in /workspace/kaggle/kaggle.json."

chmod 600 /home/gitpod/.kaggle/kaggle.json
