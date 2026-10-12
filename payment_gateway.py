import razorpay

RAZORPAY_KEY_ID = "YOUR_TEST_KEY_ID"
RAZORPAY_KEY_SECRET = "YOUR_TEST_KEY_SECRET"

client = razorpay.Client(
    auth=(
        RAZORPAY_KEY_ID,
        RAZORPAY_KEY_SECRET
    )
)