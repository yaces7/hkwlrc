import os

def check_dataset():
    base_dir = 'dataset'
    categories = ['normal_swimming', 'drowning']
    
    # Ana klasor kontrolu
    if not os.path.exists(base_dir):
        print(f"'{base_dir}' klasoru bulunamadi!")
        return False
        
    total_images = 0
    for category in categories:
        category_path = os.path.join(base_dir, category)
        if not os.path.exists(category_path):
            print(f"'{category}' klasoru bulunamadi!")
            return False
            
        images = os.listdir(category_path)
        num_images = len(images)
        print(f"{category}: {num_images} goruntu")
        total_images += num_images
        
    print(f"\nToplam: {total_images} goruntu")
    return total_images > 0

if __name__ == "__main__":
    check_dataset()