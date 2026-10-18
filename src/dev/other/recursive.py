def total(nums):
    if not nums:              # base case: empty list sums to 0
        return 0
    tot = nums[0] + total(nums[1:]) # this is where recursion happens
    # instead of tot = num[0] + num[1] and loop
    # we call total(nums[1:]) - That's the tricky part
    print(tot)
    return tot   # trust total() to sum "the rest"

numbers = [2,3,4,5]

total(numbers)