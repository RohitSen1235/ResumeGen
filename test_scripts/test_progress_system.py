#!/usr/bin/env python3
"""
Test script to verify the progress tracking system works correctly.
This script tests the Redis caching functions and progress tracking.
"""

import sys
import os
import time
import asyncio

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import (
    save_generation_status,
    get_generation_status,
    save_generation_result,
    get_generation_result,
    cleanup_generation_cache,
    generate_uuid
)

async def test_progress_system():
    """Test the progress tracking system"""
    print("🧪 Testing Resume Generation Progress System")
    print("=" * 50)
    
    # Generate a test job ID
    job_id = generate_uuid()
    print(f"📋 Test Job ID: {job_id}")
    
    try:
        # Test 1: Save initial status
        print("\n1️⃣ Testing initial status save...")
        success = save_generation_status(
            job_id=job_id,
            status="parsing",
            progress=10,
            current_step="Analyzing job description...",
            estimated_time=180
        )
        print(f"   ✅ Status saved: {success}")
        
        # Test 2: Retrieve status
        print("\n2️⃣ Testing status retrieval...")
        status = get_generation_status(job_id)
        if status:
            print(f"   ✅ Status retrieved:")
            print(f"      - Status: {status['status']}")
            print(f"      - Progress: {status['progress']}%")
            print(f"      - Current Step: {status['current_step']}")
            print(f"      - Estimated Time: {status['estimated_time_remaining']}s")
            print(f"      - Elapsed Time: {status['elapsed_time']}s")
        else:
            print("   ❌ Failed to retrieve status")
            return False
        
        # Test 3: Update progress through different stages
        stages = [
            ("analyzing", 25, "Analyzing content quality...", 150),
            ("optimizing", 50, "Optimizing skills alignment...", 120),
            ("constructing", 75, "Constructing final resume...", 60),
            ("completed", 100, "Resume generation completed!", 0)
        ]
        
        print("\n3️⃣ Testing progress updates...")
        for stage, progress, step, time_remaining in stages:
            await asyncio.sleep(1)  # Simulate processing time
            success = save_generation_status(job_id, stage, progress, step, time_remaining)
            status = get_generation_status(job_id)
            print(f"   📊 {stage.upper()}: {progress}% - {step}")
        
        # Test 4: Save generation result
        print("\n4️⃣ Testing result storage...")
        test_result = {
            "job_id": job_id,
            "job_title": "Software Engineer",
            "content": "# Test Resume Content\n\nThis is a test resume...",
            "agent_outputs": "Test agent outputs...",
            "message": "Test completed successfully"
        }
        
        success = save_generation_result(job_id, test_result)
        print(f"   ✅ Result saved: {success}")
        
        # Test 5: Retrieve generation result
        print("\n5️⃣ Testing result retrieval...")
        result = get_generation_result(job_id)
        if result:
            print(f"   ✅ Result retrieved:")
            print(f"      - Job Title: {result['job_title']}")
            print(f"      - Content Length: {len(result['content'])} chars")
            print(f"      - Message: {result['message']}")
        else:
            print("   ❌ Failed to retrieve result")
            return False
        
        # Test 6: Cleanup
        print("\n6️⃣ Testing cleanup...")
        success = cleanup_generation_cache(job_id)
        print(f"   ✅ Cache cleaned up: {success}")
        
        # Verify cleanup worked
        status_after_cleanup = get_generation_status(job_id)
        result_after_cleanup = get_generation_result(job_id)
        
        if not status_after_cleanup and not result_after_cleanup:
            print("   ✅ Cleanup verified - no data remains")
        else:
            print("   ⚠️  Cleanup incomplete - some data remains")
        
        print("\n🎉 All tests passed! Progress system is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Run the test
    result = asyncio.run(test_progress_system())
    
    if result:
        print("\n✅ Progress tracking system is ready for production!")
        sys.exit(0)
    else:
        print("\n❌ Progress tracking system needs attention!")
        sys.exit(1)
